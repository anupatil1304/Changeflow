from flask import Blueprint, jsonify, g
from sqlalchemy import func, text
from extensions import db
from models import Request as RequestModel, Development, ActivityLog, Approval, Platform
from utils.decorators import token_required
from utils.visibility import get_developer_visible_request_ids

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/api/dashboard")


def _scoped_query():
    q = RequestModel.query
    role = g.current_role

    if role == "Requester":
        q = q.filter(RequestModel.RequesterID == g.current_user.UserID)

    elif role == "Developer":
        visible_ids = get_developer_visible_request_ids(
            Development.query.all(),
            g.current_user.UserID,
        )
        q = q.filter(RequestModel.RequestID.in_(visible_ids or [-1]))

    return q


@dashboard_bp.route("/kpis", methods=["GET"])
@token_required
def kpis():
    base = _scoped_query()

    total = base.count()

    open_ = base.filter(
        RequestModel.Status.notin_(["Closed", "Rejected"])
    ).count()

    in_approval = base.filter(
        RequestModel.Status.in_(
            ["Pending Platform Approval", "Pending PGC Approval"]
        )
    ).count()

    in_dev = base.filter(
        RequestModel.Status.in_(
            ["BRD Submission", "In Development", "QA", "UAT"]
        )
    ).count()

    closed = base.filter(
        RequestModel.Status.in_(["Closed", "Production"])
    ).count()

    rejected = base.filter(
        RequestModel.Status == "Rejected"
    ).count()

    return jsonify({
        "total": total,
        "open": open_,
        "inApproval": in_approval,
        "inDevelopment": in_dev,
        "closed": closed,
        "rejected": rejected,
    })


@dashboard_bp.route("/status-chart", methods=["GET"])
@token_required
def status_chart():

    rows = (
        _scoped_query()
        .with_entities(
            RequestModel.Status,
            func.count(RequestModel.RequestID)
        )
        .group_by(RequestModel.Status)
        .all()
    )

    return jsonify([
        {
            "status": status,
            "count": count
        }
        for status, count in rows
    ])


@dashboard_bp.route("/platform-chart", methods=["GET"])
@token_required
def platform_chart():

    rows = (
        _scoped_query()
        .join(
            Platform,
            RequestModel.PlatformID == Platform.PlatformID
        )
        .with_entities(
            Platform.PlatformName,
            func.count(RequestModel.RequestID)
        )
        .group_by(Platform.PlatformName)
        .all()
    )

    return jsonify([
        {
            "platform": platform,
            "count": count
        }
        for platform, count in rows
    ])


@dashboard_bp.route("/priority-chart", methods=["GET"])
@token_required
def priority_chart():

    rows = (
        _scoped_query()
        .with_entities(
            RequestModel.Priority,
            func.count(RequestModel.RequestID)
        )
        .group_by(RequestModel.Priority)
        .all()
    )

    return jsonify([
        {
            "priority": priority,
            "count": count
        }
        for priority, count in rows
    ])


@dashboard_bp.route("/monthly-trend", methods=["GET"])
@token_required
def monthly_trend():

    try:
        sql = text("""
        SELECT
            LEFT(CONVERT(VARCHAR(7), CreatedDate, 120), 7) AS month,
            COUNT(RequestID) AS count
        FROM ChangeFlowRequests
        GROUP BY LEFT(CONVERT(VARCHAR(7), CreatedDate, 120), 7)
        ORDER BY month
    """)
        result = db.session.execute(sql)

        rows = []

        for row in result:
            rows.append({
                "month": row[0],
                "count": row[1]
            })

        return jsonify(rows)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@dashboard_bp.route("/sla-aging", methods=["GET"])
@token_required
def sla_aging():

    from datetime import datetime

    buckets = {
        "0-2 days": 0,
        "3-5 days": 0,
        "6-10 days": 0,
        "10+ days": 0
    }

    requests = (
        _scoped_query()
        .filter(
            RequestModel.Status.notin_(
                ["Closed", "Rejected", "Production"]
            )
        )
        .all()
    )

    for r in requests:

        age = (datetime.utcnow() - r.CreatedDate).days

        if age <= 2:
            buckets["0-2 days"] += 1

        elif age <= 5:
            buckets["3-5 days"] += 1

        elif age <= 10:
            buckets["6-10 days"] += 1

        else:
            buckets["10+ days"] += 1

    return jsonify(buckets)


@dashboard_bp.route("/developer-workload", methods=["GET"])
@token_required
def developer_workload():

    rows = (
        db.session.query(
            Development.AssignedTo,
            func.count(Development.DevID)
        )
        .filter(Development.Progress < 100)
        .group_by(Development.AssignedTo)
        .all()
    )

    from models import User

    result = []

    for user_id, count in rows:

        user = User.query.get(user_id) if user_id else None

        result.append({
            "developer": user.Name if user else "Unassigned",
            "activeItems": count
        })

    return jsonify(result)


@dashboard_bp.route("/recent-activities", methods=["GET"])
@token_required
def recent_activities():

    rows = (
        ActivityLog.query
        .order_by(ActivityLog.Timestamp.desc())
        .limit(15)
        .all()
    )

    return jsonify([
        a.to_dict()
        for a in rows
    ])


@dashboard_bp.route("/pending-approvals", methods=["GET"])
@token_required
def pending_approvals():

    if g.current_role == "Platform Owner":

        rows = (
            Approval.query
            .join(
                RequestModel,
                Approval.RequestID == RequestModel.RequestID
            )
            .filter(
                Approval.Level == "Platform Owner",
                Approval.Decision == "Pending"
            )
            .order_by(
                RequestModel.CreatedDate.desc()
            )
            .all()
        )

    elif g.current_role == "PGC":

        rows = (
            Approval.query
            .join(
                RequestModel,
                Approval.RequestID == RequestModel.RequestID
            )
            .filter(
                Approval.Level == "PGC",
                Approval.Decision == "Pending"
            )
            .order_by(
                RequestModel.CreatedDate.desc()
            )
            .all()
        )

    elif g.current_role == "Admin":

        rows = (
            Approval.query
            .join(
                RequestModel,
                Approval.RequestID == RequestModel.RequestID
            )
            .filter(
                Approval.Decision == "Pending"
            )
            .order_by(
                RequestModel.CreatedDate.desc()
            )
            .all()
        )

    else:
        return jsonify([])

    return jsonify([a.request.to_dict()for a in rows ])