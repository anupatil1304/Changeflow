from datetime import datetime
from flask import Blueprint, request, jsonify, g
from extensions import db
from models import Development, Request as RequestModel, ActivityLog
from utils.decorators import token_required, roles_required

development_bp = Blueprint("development", __name__, url_prefix="/api/development")


def _parse_date(value):
    if not value:
        return None
    return datetime.strptime(value, "%Y-%m-%d").date()


@development_bp.route("", methods=["GET"])
@token_required
def list_development():
    """
    Development Tracking screen: Owner, Dates, Progress.
    Developer sees only items assigned to them; Admin/PGC see all.
    """
    q = Development.query
    if g.current_role == "Developer":
        q = q.filter((Development.AssignedTo.is_(None)) | (Development.AssignedTo == g.current_user.UserID))

    result = []
    for d in q.all():
        row = d.to_dict()
        if d.request:
            row["requestType"] = d.request.Type
            row["platformName"] = d.request.platform.PlatformName if d.request.platform else None
            row["priority"] = d.request.Priority
            row["status"] = d.request.Status
            row["description"] = d.request.Description
        result.append(row)
    return jsonify(result)


@development_bp.route("/<int:request_id>", methods=["GET"])
@token_required
def get_development(request_id):
    dev = Development.query.filter_by(RequestID=request_id).first_or_404()
    return jsonify(dev.to_dict())


@development_bp.route("/<int:request_id>", methods=["PUT"])
@token_required
@roles_required("Developer", "Admin")
def update_development(request_id):
    """Update Owner (AssignedTo), StartDate, TargetDate, CompletionDate, Progress"""
    dev = Development.query.filter_by(RequestID=request_id).first_or_404()
    data = request.get_json(silent=True) or {}

    if "assignedTo" in data:
        dev.AssignedTo = data["assignedTo"]
    if "startDate" in data:
        dev.StartDate = _parse_date(data["startDate"])
    # Target date can only be set once
    if "targetDate" in data and dev.TargetDate is None:
        dev.TargetDate = _parse_date(data["targetDate"])
    if "completionDate" in data:
        dev.CompletionDate = _parse_date(data["completionDate"])

    req = RequestModel.query.get(request_id)
    # Progress-driven status transitions down the workflow
    status = data.get("status")

    if status == "BRD Submission":
        req.Status = "BRD Submission"
        dev.Progress = 20

    elif status == "In Development":
        req.Status = "In Development"
        dev.Progress = 40

    elif status == "QA":
        req.Status = "QA"
        dev.Progress = 60

    elif status == "Testing/UAT":
        req.Status = "Testing/UAT"
        dev.Progress = 80

    elif status == "Production":
        req.Status = "Production"
        dev.Progress = 100
        dev.CompletionDate = datetime.now().date()

    elif status == "Closed":
        req.Status = "Closed"
        dev.Progress = 100

    db.session.add(ActivityLog(RequestID=request_id, UserID=g.current_user.UserID,
                                Action=f"Status changed to {req.Status} ({dev.Progress}% complete)"))
    db.session.commit()
    return jsonify({"development": dev.to_dict(), "request": req.to_dict()})
