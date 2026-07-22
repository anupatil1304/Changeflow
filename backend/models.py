"""
SQLAlchemy models - map 1:1 to backend/database/schema_sqlserver.sql
(table/column names match the Database Design section of the Application
Design Pack so the ORM layer and the DBA-facing DDL never drift apart).
"""
from datetime import datetime,date
from extensions import db


class Role(db.Model):
    __tablename__ = "ChangeFlowRoles"
    RoleID = db.Column(db.Integer, primary_key=True)
    RoleName = db.Column(db.String(50), nullable=False, unique=True)

    users = db.relationship("User", backref="role", lazy=True)

class Business(db.Model):
    __tablename__ = "ChangeFlowBusiness"

    BusinessID = db.Column(db.Integer, primary_key=True)
    BusinessName = db.Column(db.String(100), nullable=False, unique=True)
    IsActive = db.Column(db.Boolean, default=True)

    def to_dict(self):
        return {
            "businessId": self.BusinessID,
            "businessName": self.BusinessName,
            "isActive": self.IsActive
        }

class Platform(db.Model):
    __tablename__ = "ChangeFlowPlatforms"

    PlatformID = db.Column(db.Integer, primary_key=True)
    PlatformName = db.Column(db.String(150), nullable=False, unique=True)
    OwnerID = db.Column(db.Integer, db.ForeignKey("ChangeFlowUsers.UserID"), nullable=True)
    IsActive = db.Column(db.Boolean, nullable=False, default=True)
    requests = db.relationship("Request", backref="platform", lazy=True)

class User(db.Model):
    __tablename__ = "ChangeFlowUsers"
    UserID = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(150), nullable=False)
    Email = db.Column(db.String(150), nullable=False, unique=True)
    PasswordHash = db.Column(db.String(255), nullable=False)
    RoleID = db.Column(db.Integer, db.ForeignKey("ChangeFlowRoles.RoleID"), nullable=False)
    PlatformID = db.Column(db.Integer, db.ForeignKey("ChangeFlowPlatforms.PlatformID"), nullable=True)
    BusinessID = db.Column(
        db.Integer,
        db.ForeignKey("ChangeFlowBusiness.BusinessID"),
        nullable=True
    )

    business = db.relationship("Business")
    Status = db.Column(db.String(20), nullable=False, default="Active")
    CreatedDate = db.Column(
        db.DateTime,
        default=datetime.now
    )

    def to_dict(self):
        return {
            "userId": self.UserID,
            "name": self.Name,
            "email": self.Email,
            "role": self.role.RoleName if self.role else None,
            "roleId": self.RoleID,
            "platformId": self.PlatformID,
            "platformName": self.platform_ref.PlatformName if self.platform_ref else None,
            "businessId": self.BusinessID,
            "businessName": self.business.BusinessName if self.business else None,
            "status": self.Status,
        }


# Backref from User -> Platform for the platform a user belongs to
User.platform_ref = db.relationship("Platform", foreign_keys=[User.PlatformID])


class Category(db.Model):
    __tablename__ = "ChangeFlowCategories"
    CategoryID = db.Column(db.Integer, primary_key=True)
    CategoryName = db.Column(db.String(100), nullable=False, unique=True)
    Type = db.Column(db.String(20), nullable=False, default="Enhancement")
    IsActive = db.Column(db.Boolean, nullable=False, default=True)


class Request(db.Model):
    __tablename__ = "ChangeFlowRequests"
    RequestID = db.Column(db.Integer, primary_key=True)
    Type = db.Column(db.String(20), nullable=False)  # Project / Enhancement
    PlatformID = db.Column(db.Integer, db.ForeignKey("ChangeFlowPlatforms.PlatformID"), nullable=False)
    CategoryID = db.Column(db.Integer, db.ForeignKey("ChangeFlowCategories.CategoryID"), nullable=True)
    RequesterID = db.Column(db.Integer, db.ForeignKey("ChangeFlowUsers.UserID"), nullable=False)
    Priority = db.Column(db.String(20), nullable=False)  # Low/Medium/High/Critical
    Description = db.Column(db.String(2000), nullable=False)
    AttachmentPath = db.Column(db.String(500), nullable=True)
    Status = db.Column(db.String(40), nullable=False, default="Pending Platform Approval")
    CreatedDate = db.Column(
    db.DateTime,
    default=datetime.now
)

    requester = db.relationship("User", foreign_keys=[RequesterID])
    category = db.relationship("Category", foreign_keys=[CategoryID])
    approvals = db.relationship("Approval", backref="request", lazy=True,
                                 cascade="all, delete-orphan")
    activity_log = db.relationship("ActivityLog", backref="request", lazy=True,
                                   cascade="all, delete-orphan")
    development = db.relationship("Development", backref="request", uselist=False,
                                   cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "requestId": self.RequestID,
            "type": self.Type,
            "platformId": self.PlatformID,
            "platformName": self.platform.PlatformName if self.platform else None,
            "categoryId": self.CategoryID,
            "categoryName": self.category.CategoryName if self.category else None,
            "requesterId": self.RequesterID,
            "requesterName": self.requester.Name if self.requester else None,
            "priority": self.Priority,
            "description": self.Description,
            "attachmentPath": self.AttachmentPath,
            "status": self.Status,
            "createdDate": self.CreatedDate.isoformat() if self.CreatedDate else None,
        }


class Approval(db.Model):
    __tablename__ = "ChangeFlowApprovals"
    ApprovalID = db.Column(db.Integer, primary_key=True)
    RequestID = db.Column(db.Integer, db.ForeignKey("ChangeFlowRequests.RequestID"), nullable=False)
    Level = db.Column(db.String(20), nullable=False)  # Platform Owner / PGC
    ApproverID = db.Column(db.Integer, db.ForeignKey("ChangeFlowUsers.UserID"), nullable=False)
    Decision = db.Column(db.String(20), nullable=False, default="Pending")
    Remarks = db.Column(db.String(1000), nullable=True)
    Date = db.Column(db.DateTime, nullable=True)

    approver = db.relationship("User", foreign_keys=[ApproverID])

    def to_dict(self):
        return {
            "approvalId": self.ApprovalID,
            "requestId": self.RequestID,
            "level": self.Level,
            "approverId": self.ApproverID,
            "approverName": self.approver.Name if self.approver else None,
            "decision": self.Decision,
            "remarks": self.Remarks,
            "date": self.Date.isoformat() if self.Date else None,
        }


class Development(db.Model):
    __tablename__ = "ChangeFlowDevelopment"
    DevID = db.Column(db.Integer, primary_key=True)
    RequestID = db.Column(db.Integer, db.ForeignKey("ChangeFlowRequests.RequestID"), nullable=False, unique=True)
    AssignedTo = db.Column(db.Integer, db.ForeignKey("ChangeFlowUsers.UserID"), nullable=True)
    StartDate = db.Column(db.Date, nullable=True)
    TargetDate = db.Column(db.Date, nullable=True)
    CompletionDate = db.Column(db.Date, nullable=True)
    Progress = db.Column(db.Integer, nullable=False, default=0)

    assignee = db.relationship("User", foreign_keys=[AssignedTo])

    def to_dict(self):
        req = self.request

    # Due Status
        if req and req.Status in ["Production", "Closed"]:
            dueStatus = "Completed"

        elif self.TargetDate:
            days_left = (self.TargetDate - date.today()).days

            if days_left < 0:
                dueStatus = "Overdue"
            elif days_left <= 2:
                dueStatus = "Due Soon"
            else:
                dueStatus = "On Track"

        else:
            dueStatus = "No Target"

        return {
            "devId": self.DevID,
            "requestId": self.RequestID,
            "platformName": req.platform.PlatformName if req and req.platform else None,
            "status": req.Status if req else None,
            "assignedTo": self.AssignedTo,
            "assigneeName": self.assignee.Name if self.assignee else None,
            "startDate": self.StartDate.isoformat() if self.StartDate else None,
            "targetDate": self.TargetDate.isoformat() if self.TargetDate else None,
            "completionDate": self.CompletionDate.isoformat() if self.CompletionDate else None,
            "progress": self.Progress,
            "dueStatus": dueStatus,
    }


class ActivityLog(db.Model):
    __tablename__ = "ChangeFlowActivityLog"

    ActivityID = db.Column(db.Integer, primary_key=True)

    RequestID = db.Column(
        db.Integer,
        db.ForeignKey("ChangeFlowRequests.RequestID"),
        nullable=True
    )

    UserID = db.Column(
        db.Integer,
        db.ForeignKey("ChangeFlowUsers.UserID"),
        nullable=True
    )

    Action = db.Column(db.String(200), nullable=False)

    Timestamp = db.Column(
        db.DateTime,
        default=datetime.now
    )

    user = db.relationship(
        "User",
        foreign_keys=[UserID]
    )

    def to_dict(self):
        return {
            "activityId": self.ActivityID,
            "requestId": self.RequestID,
            "userName": self.user.Name if self.user else "System",
            "action": self.Action,
            "timestamp": self.Timestamp.isoformat() if self.Timestamp else None,
        }