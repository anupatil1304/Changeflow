from flask import Blueprint, jsonify
from models import Platform, Category, User, Role
from utils.decorators import token_required

lookups_bp = Blueprint("lookups", __name__, url_prefix="/api")


@lookups_bp.route("/platforms", methods=["GET"])
@token_required
def list_platforms_lookup():
    """Read-only platform list for dropdowns (Raise Request, Reports filters, etc.)"""
    platforms = Platform.query.filter(Platform.IsActive == True).order_by(Platform.PlatformName).all()
    return jsonify([{"platformId": p.PlatformID, "platformName": p.PlatformName}
                     for p in platforms])


@lookups_bp.route("/categories", methods=["GET"])
@token_required
def list_categories_lookup():
    categories = Category.query.filter(Category.IsActive == True).order_by(Category.CategoryName).all()
    return jsonify([{"categoryId": c.CategoryID, "categoryName": c.CategoryName, "type": c.Type}
                     for c in categories])


@lookups_bp.route("/developers", methods=["GET"])
@token_required
def list_developers_lookup():
    """Developer list for the Development Tracking 'Owner' assignment dropdown"""
    devs = (User.query.join(Role, User.RoleID == Role.RoleID)
            .filter(Role.RoleName == "Developer").all())
    return jsonify([{"userId": d.UserID, "name": d.Name} for d in devs])
