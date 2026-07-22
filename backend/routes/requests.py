import os
import uuid
from datetime import datetime
from flask import Blueprint, request, jsonify, g, current_app, send_from_directory
from extensions import db
from models import Request as RequestModel, Approval, ActivityLog, Platform, Category
from utils.decorators import token_required, roles_required
from utils.visibility import get_developer_visible_request_ids

requests_bp = Blueprint("requests", __name__, url_prefix="/api/requests")

ALLOWED_EXTENSIONS = {"pdf", "png", "jpg", "jpeg", "docx", "xlsx", "txt", "csv"}


def _allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def _log(request_id, user_id, action):
    db.session.add(ActivityLog(RequestID=request_id, UserID=user_id, Action=action))


@requests_bp.route("", methods=["POST"])
@token_required
@roles_required("Requester", "Admin")
def create_request():
    """Raise Request screen: Project/Enhancement, Platform, Priority, Description, Attachment"""
    form = request.form if request.form else (request.get_json(silent=True) or {})

    required = ["type", "platformId", "priority", "description"]
    missing = [f for f in required if not form.get(f)]
    if missing:
        return jsonify({"error": f"Missing required fields: {', '.join(missing)}"}), 400

    platform = Platform.query.get(int(form["platformId"]))
    if not platform:
        return jsonify({"error": "Invalid platformId"}), 400

    attachment_path = None
    file = request.files.get("attachment")
    if file and file.filename:
        if not _allowed_file(file.filename):
            return jsonify({"error": "Attachment file type not allowed"}), 400
        os.makedirs(current_app.config["UPLOAD_FOLDER"], exist_ok=True)
        safe_name = f"{uuid.uuid4().hex}_{file.filename}"
        file.save(os.path.join(current_app.config["UPLOAD_FOLDER"], safe_name))
        attachment_path = safe_name

    new_req = RequestModel(
        Type=form["type"],
        PlatformID=platform.PlatformID,
        CategoryID=form.get("categoryId") or None,
        RequesterID=g.current_user.UserID,
        Priority=form["priority"],
        Description=form["description"],
        AttachmentPath=attachment_path,
        Status="Pending Platform Approval",
    )
    db.session.add(new_req)
    db.session.flush()  # get RequestID

    # Auto-create the first approval step for the Platform Owner
    db.session.add(Approval(
        RequestID=new_req.RequestID,
        Level="Platform Owner",
        ApproverID=platform.OwnerID or g.current_user.UserID,
        Decision="Pending",
    ))
    _log(new_req.RequestID, g.current_user.UserID, "Request raised")
    db.session.commit()

    return jsonify(new_req.to_dict()), 201


@requests_bp.route("", methods=["GET"])
@token_required
def list_requests():
    """
    My Requests screen: Search, Status, Timeline.
    Scope follows the Role & Permission Matrix -> Reports row:
      Requester: Own | Platform Owner: Platform | PGC: All | Developer: Assigned | Admin: All
    """
    role = g.current_role
    q = RequestModel.query

    if role == "Requester":
        q = q.filter(RequestModel.RequesterID == g.current_user.UserID)
    elif role == "Developer":
        from models import Development
        visible_ids = get_developer_visible_request_ids(
            Development.query.all(),
            g.current_user.UserID,
        )
        q = q.filter(RequestModel.RequestID.in_(visible_ids or [-1]))
    # PGC / Admin -> no filter (All)

    search = request.args.get("search")
    status = request.args.get("status")
    if search:
        q = q.filter(RequestModel.Description.ilike(f"%{search}%"))
    if status:
        q = q.filter(RequestModel.Status == status)

    q = q.order_by(RequestModel.CreatedDate.desc())
    return jsonify([r.to_dict() for r in q.all()])


@requests_bp.route("/<int:request_id>", methods=["GET"])
@token_required
def get_request(request_id):
    req = RequestModel.query.get_or_404(request_id)
    data = req.to_dict()
    data["approvals"] = [a.to_dict() for a in
                          Approval.query.filter_by(RequestID=request_id).order_by(Approval.ApprovalID).all()]
    data["development"] = req.development.to_dict() if req.development else None
    data["timeline"] = [a.to_dict() for a in
                         ActivityLog.query.filter_by(RequestID=request_id)
                         .order_by(ActivityLog.Timestamp).all()]
    return jsonify(data)


@requests_bp.route("/<int:request_id>", methods=["DELETE"])
@token_required
def delete_request(request_id):
    req = RequestModel.query.get_or_404(request_id)

    if req.RequesterID != g.current_user.UserID:
        return jsonify({"error": "Only the original requester can delete this request."}), 403

    platform_action = Approval.query.filter_by(
        RequestID=request_id,
        Level="Platform Owner",
    ).first()

    if not platform_action or platform_action.Decision != "Pending" or req.Status != "Pending Platform Approval":
        return jsonify({
            "error": "This request can no longer be deleted because the Platform Owner has already taken action."
        }), 403

    db.session.delete(req)
    db.session.commit()

    return jsonify({"message": "Request deleted."}), 200


@requests_bp.route("/<int:request_id>/attachment", methods=["GET"])
@token_required
def download_attachment(request_id):
    req = RequestModel.query.get_or_404(request_id)
    if not req.AttachmentPath:
        return jsonify({"error": "No attachment on this request"}), 404
    return send_from_directory(current_app.config["UPLOAD_FOLDER"], req.AttachmentPath)
