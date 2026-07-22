from datetime import datetime
from flask import Blueprint, request, jsonify, g
from extensions import db
from models import Request as RequestModel, Approval, ActivityLog
from utils.decorators import token_required, roles_required

approvals_bp = Blueprint("approvals", __name__, url_prefix="/api/approvals")


def _log(request_id, user_id, action):
    db.session.add(ActivityLog(RequestID=request_id, UserID=user_id, Action=action))


def _decide(request_id, level, next_status_approve, next_status_reject):
    """Shared logic for both approval levels: Approve/Reject, Remarks"""
    data = request.get_json(silent=True) or {}
    decision = data.get("decision")
    remarks = data.get("remarks", "")

    if decision not in ("Approved", "Rejected"):
        return jsonify({"error": "decision must be 'Approved' or 'Rejected'"}), 400

    if decision == "Rejected" and not remarks.strip():
        return jsonify({"error": "Remarks are required when rejecting a request."}), 400

    req = RequestModel.query.get_or_404(request_id)
    approval = Approval.query.filter_by(RequestID=request_id, Level=level).order_by(
        Approval.ApprovalID.desc()).first()
    if not approval:
        return jsonify({"error": f"No pending {level} approval found for this request"}), 404
    if approval.Decision != "Pending":
        return jsonify({"error": f"This request has already been {approval.Decision.lower()} at {level} level"}), 409

    approval.Decision = decision
    approval.Remarks = remarks
    approval.ApproverID = g.current_user.UserID
    approval.Date = datetime.utcnow()

    if decision == "Approved":
        req.Status = next_status_approve
        # Moving from Platform Owner -> PGC: open the next pending approval step
        if level == "Platform Owner":
            db.session.add(Approval(RequestID=request_id, Level="PGC",
                                     ApproverID=g.current_user.UserID, Decision="Pending"))
        # Moving from PGC -> Development: create the Development tracking row
        if level == "PGC":
            from models import Development
            if not Development.query.filter_by(RequestID=request_id).first():
                db.session.add(Development(RequestID=request_id, Progress=0))
    else:
        req.Status = next_status_reject

    _log(request_id, g.current_user.UserID, f"{level} decision: {decision}")
    db.session.commit()
    return jsonify(req.to_dict())


@approvals_bp.route("/platform-owner", methods=["GET"])
@token_required
@roles_required("Platform Owner", "Admin")
def pending_platform_owner():
    """Platform Owner Approval screen: list of requests awaiting this platform owner"""
    q = Approval.query.filter_by(Level="Platform Owner", Decision="Pending")
    return jsonify([a.request.to_dict() for a in q.all()])


@approvals_bp.route("/platform-owner/<int:request_id>", methods=["POST"])
@token_required
@roles_required("Platform Owner", "Admin")
def decide_platform_owner(request_id):
    """Approve/Reject with Remarks -> moves request to 'Pending PGC Approval' or 'Rejected'"""
    return _decide(request_id, "Platform Owner", "Pending PGC Approval", "Rejected")


@approvals_bp.route("/pgc", methods=["GET"])
@token_required
@roles_required("PGC", "Admin")
def pending_pgc():
    """PGC Review screen: list of requests awaiting PGC decision"""
    q = Approval.query.filter_by(Level="PGC", Decision="Pending")
    return jsonify([a.request.to_dict() for a in q.all()])


@approvals_bp.route("/pgc/<int:request_id>", methods=["POST"])
@token_required
@roles_required("PGC", "Admin")
def decide_pgc(request_id):
    """Approve/Reject with Remarks -> moves request to 'In Development' or 'Rejected'"""
    return _decide(request_id, "PGC", "In Development", "Rejected")
