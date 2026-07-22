from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash
from extensions import db
from models import Platform, User, Category, Role, Business
from sqlalchemy import case
from utils.decorators import token_required, roles_required

admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")

# ---------------------------------------------------------------- Platforms
@admin_bp.route("/platforms", methods=["GET"])
@token_required
@roles_required("Admin")
def list_platforms():
    return jsonify([
    {
        "platformId": p.PlatformID,
        "platformName": p.PlatformName,

        "isActive": p.IsActive
    }
    for p in Platform.query.order_by(
    Platform.IsActive.desc(),
    Platform.PlatformName.asc()
).all()
])


@admin_bp.route("/platforms", methods=["POST"])
@token_required
@roles_required("Admin")
def create_platform():
    data = request.get_json(silent=True) or {}
    if not data.get("platformName"):
        return jsonify({"error": "platformName is required"}), 400
    p = Platform(
    PlatformName=data["platformName"],

    IsActive=data.get("isActive", True)
)
    db.session.add(p)
    db.session.commit()
    return jsonify({"platformId": p.PlatformID, "platformName": p.PlatformName}), 201


@admin_bp.route("/platforms/<int:platform_id>", methods=["PUT"])
@token_required
@roles_required("Admin")
def update_platform(platform_id):

    p = Platform.query.get_or_404(platform_id)

    data = request.get_json(silent=True) or {}

    p.PlatformName = data.get("platformName", p.PlatformName)

    if "isActive" in data:
        p.IsActive = bool(data.get("isActive"))

    db.session.commit()

    return jsonify({
        "platformId": p.PlatformID,
        "platformName": p.PlatformName,
        "isActive": p.IsActive
    })

@admin_bp.route("/platforms/<int:platform_id>/status", methods=["PUT"])
@token_required
@roles_required("Admin")
def update_platform_status(platform_id):
    p = Platform.query.get_or_404(platform_id)
    data = request.get_json(silent=True) or {}
    p.IsActive = bool(data.get("isActive", p.IsActive))
    db.session.commit()
    return jsonify({"platformId": p.PlatformID, "isActive": p.IsActive})


# ---------------------------------------------------------------- Users
# @admin_bp.route("/users", methods=["GET"])
# @token_required
# @roles_required("Admin")
# def list_users():

#     users = User.query.order_by(
#         case(
#             (User.Status == "Active", 1),
#             else_=0
#         ).desc(),
#         User.Name.asc()
#     ).all()

#     return jsonify([u.to_dict() for u in users])

from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash
from extensions import db
from models import Platform, User, Category, Role, Business
from sqlalchemy import case
from utils.decorators import token_required, roles_required

admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")

# ---------------------------------------------------------------- Platforms
@admin_bp.route("/platforms", methods=["GET"])
@token_required
@roles_required("Admin")
def list_platforms():
    return jsonify([
    {
        "platformId": p.PlatformID,
        "platformName": p.PlatformName,

        "isActive": p.IsActive
    }
    for p in Platform.query.order_by(
    Platform.IsActive.desc(),
    Platform.PlatformName.asc()
).all()
])


@admin_bp.route("/platforms", methods=["POST"])
@token_required
@roles_required("Admin")
def create_platform():
    data = request.get_json(silent=True) or {}
    if not data.get("platformName"):
        return jsonify({"error": "platformName is required"}), 400
    p = Platform(
    PlatformName=data["platformName"],

    IsActive=data.get("isActive", True)
)
    db.session.add(p)
    db.session.commit()
    return jsonify({"platformId": p.PlatformID, "platformName": p.PlatformName}), 201


@admin_bp.route("/platforms/<int:platform_id>", methods=["PUT"])
@token_required
@roles_required("Admin")
def update_platform(platform_id):

    p = Platform.query.get_or_404(platform_id)

    data = request.get_json(silent=True) or {}

    p.PlatformName = data.get("platformName", p.PlatformName)

    if "isActive" in data:
        p.IsActive = bool(data.get("isActive"))

    db.session.commit()

    return jsonify({
        "platformId": p.PlatformID,
        "platformName": p.PlatformName,
        "isActive": p.IsActive
    })

@admin_bp.route("/platforms/<int:platform_id>/status", methods=["PUT"])
@token_required
@roles_required("Admin")
def update_platform_status(platform_id):
    p = Platform.query.get_or_404(platform_id)
    data = request.get_json(silent=True) or {}
    p.IsActive = bool(data.get("isActive", p.IsActive))
    db.session.commit()
    return jsonify({"platformId": p.PlatformID, "isActive": p.IsActive})


# ---------------------------------------------------------------- Users
# @admin_bp.route("/users", methods=["GET"])
# @token_required
# @roles_required("Admin")
# def list_users():

#     users = User.query.order_by(
#         case(
#             (User.Status == "Active", 1),
#             else_=0
#         ).desc(),
#         User.Name.asc()
#     ).all()

#     return jsonify([u.to_dict() for u in users])
@admin_bp.route("/users", methods=["GET"])
@token_required
@roles_required("Admin")
def list_users():

    users = [u.to_dict() for u in User.query.all()]

    users.sort(
        key=lambda x: (
            x["status"] != "Active",
            x["name"].lower()
        )
    )

    print("SORTED")
    for u in users:
        print(u["name"], u["status"])

    return jsonify(users)

    
@admin_bp.route("/users", methods=["POST"])
@token_required
@roles_required("Admin")
def create_user():
    data = request.get_json(silent=True) or {}
    required = ["name", "email", "password", "roleId"]
    missing = [f for f in required if not data.get(f)]
    if missing:
        return jsonify({"error": f"Missing required fields: {', '.join(missing)}"}), 400
    if User.query.filter_by(Email=data["email"]).first():
        return jsonify({"error": "Email already registered"}), 409

    u = User(
        Name=data["name"], Email=data["email"],
        PasswordHash=generate_password_hash(data["password"]),
        RoleID=data["roleId"], PlatformID=data.get("platformId"),
        BusinessID=data.get("businessId"),
        Status=data.get("status", "Active"),
    )
    db.session.add(u)
    db.session.commit()
    return jsonify(u.to_dict()), 201


@admin_bp.route("/users/<int:user_id>", methods=["PUT"])
@token_required
@roles_required("Admin")
def update_user(user_id):
    u = User.query.get_or_404(user_id)
    data = request.get_json(silent=True) or {}
    u.Name = data.get("name", u.Name)
    u.Email = data.get("email", u.Email)
    u.RoleID = data.get("roleId", u.RoleID)
    u.PlatformID = data.get("platformId", u.PlatformID)
    u.BusinessID = data.get("businessId", u.BusinessID)
    u.Status = data.get("status", u.Status)
    if data.get("password"):
        u.PasswordHash = generate_password_hash(data["password"])
    db.session.commit()
    return jsonify(u.to_dict())

@admin_bp.route("/users/<int:user_id>/status", methods=["PUT"])
@token_required
@roles_required("Admin")
def update_user_status(user_id):

    u = User.query.get_or_404(user_id)

    data = request.get_json(silent=True) or {}

    u.Status = data.get("status", u.Status)

    db.session.commit()

    return jsonify({
        "userId": u.UserID,
        "status": u.Status
    })


@admin_bp.route("/users/<int:user_id>", methods=["DELETE"])
@token_required
@roles_required("Admin")
def delete_user(user_id):
    u = User.query.get_or_404(user_id)
    db.session.delete(u)
    db.session.commit()
    return jsonify({"message": "User deleted"})


# ---------------------------------------------------------------- Categories
@admin_bp.route("/categories", methods=["GET"])
@token_required
@roles_required("Admin")
def list_categories():
   return jsonify([
    {
        "categoryId": c.CategoryID,
        "categoryName": c.CategoryName,
        "type": c.Type,
        "isActive": c.IsActive
    }
    for c in Category.query.order_by(
        Category.IsActive.desc(),
        Category.CategoryName.asc()
    ).all()
])


@admin_bp.route("/categories", methods=["POST"])
@token_required
@roles_required("Admin")
def create_category():
    data = request.get_json(silent=True) or {}
    if not data.get("categoryName"):
        return jsonify({"error": "categoryName is required"}), 400
    c = Category(CategoryName=data["categoryName"], Type=data.get("type", "Enhancement"), IsActive=data.get("isActive", True))
    db.session.add(c)
    db.session.commit()
    return jsonify({"categoryId": c.CategoryID, "categoryName": c.CategoryName}), 201


@admin_bp.route("/categories/<int:category_id>", methods=["PUT"])
@token_required
@roles_required("Admin")
def update_category(category_id):

    print("UPDATE CATEGORY CALLED")   # <-- Add this line

    c = Category.query.get_or_404(category_id)

    data = request.get_json(silent=True) or {}

    c.CategoryName = data.get("categoryName", c.CategoryName)
    c.Type = data.get("type", c.Type)

    db.session.commit()

    return jsonify({
        "categoryId": c.CategoryID,
        "categoryName": c.CategoryName,
        "type": c.Type,
        "isActive": c.IsActive
    })

@admin_bp.route("/categories/<int:category_id>/status", methods=["PUT"])
@token_required
@roles_required("Admin")
def update_category_status(category_id):
    c = Category.query.get_or_404(category_id)
    data = request.get_json(silent=True) or {}
    c.IsActive = bool(data.get("isActive", c.IsActive))
    db.session.commit()
    return jsonify({"categoryId": c.CategoryID, "isActive": c.IsActive})


# ---------------------------------------------------------------- Roles (read-only lookup)
@admin_bp.route("/roles", methods=["GET"])
@token_required
@roles_required("Admin")
def list_roles():
    return jsonify([{"roleId": r.RoleID, "roleName": r.RoleName} for r in Role.query.all()])

# ---------------------------------------------------------------- Business

@admin_bp.route("/business", methods=["GET"])
@token_required
@roles_required("Admin")
def list_business():
    return jsonify([
        {
            "businessId": b.BusinessID,
            "businessName": b.BusinessName,
            "isActive": b.IsActive
        }
        for b in Business.query.order_by(Business.BusinessName).all()
    ])


@admin_bp.route("/business", methods=["POST"])
@token_required
@roles_required("Admin")
def create_business():
    data = request.get_json(silent=True) or {}

    if not data.get("businessName"):
        return jsonify({"error": "businessName is required"}), 400

    if Business.query.filter_by(BusinessName=data["businessName"]).first():
        return jsonify({"error": "Business already exists"}), 409

    b = Business(
        BusinessName=data["businessName"],
        IsActive=data.get("isActive", True)
    )

    db.session.add(b)
    db.session.commit()

    return jsonify(b.to_dict()), 201

@admin_bp.route("/users", methods=["GET"])
@token_required
@roles_required("Admin")
def list_users():

    users = [u.to_dict() for u in User.query.all()]

    users.sort(
        key=lambda u: (
            u["status"] != "Active",
            u["name"].lower()
        )
    )

    print(users)

    return jsonify(users)


@admin_bp.route("/users", methods=["POST"])
@token_required
@roles_required("Admin")
def create_user():
    data = request.get_json(silent=True) or {}
    required = ["name", "email", "password", "roleId"]
    missing = [f for f in required if not data.get(f)]
    if missing:
        return jsonify({"error": f"Missing required fields: {', '.join(missing)}"}), 400
    if User.query.filter_by(Email=data["email"]).first():
        return jsonify({"error": "Email already registered"}), 409

    u = User(
        Name=data["name"], Email=data["email"],
        PasswordHash=generate_password_hash(data["password"]),
        RoleID=data["roleId"], PlatformID=data.get("platformId"),
        BusinessID=data.get("businessId"),
        Status=data.get("status", "Active"),
    )
    db.session.add(u)
    db.session.commit()
    return jsonify(u.to_dict()), 201


@admin_bp.route("/users/<int:user_id>", methods=["PUT"])
@token_required
@roles_required("Admin")
def update_user(user_id):
    u = User.query.get_or_404(user_id)
    data = request.get_json(silent=True) or {}
    u.Name = data.get("name", u.Name)
    u.Email = data.get("email", u.Email)
    u.RoleID = data.get("roleId", u.RoleID)
    u.PlatformID = data.get("platformId", u.PlatformID)
    u.BusinessID = data.get("businessId", u.BusinessID)
    u.Status = data.get("status", u.Status)
    if data.get("password"):
        u.PasswordHash = generate_password_hash(data["password"])
    db.session.commit()
    return jsonify(u.to_dict())

@admin_bp.route("/users/<int:user_id>/status", methods=["PUT"])
@token_required
@roles_required("Admin")
def update_user_status(user_id):

    u = User.query.get_or_404(user_id)

    data = request.get_json(silent=True) or {}

    u.Status = data.get("status", u.Status)

    db.session.commit()

    return jsonify({
        "userId": u.UserID,
        "status": u.Status
    })


@admin_bp.route("/users/<int:user_id>", methods=["DELETE"])
@token_required
@roles_required("Admin")
def delete_user(user_id):
    u = User.query.get_or_404(user_id)
    db.session.delete(u)
    db.session.commit()
    return jsonify({"message": "User deleted"})


# ---------------------------------------------------------------- Categories
@admin_bp.route("/categories", methods=["GET"])
@token_required
@roles_required("Admin")
def list_categories():
   return jsonify([
    {
        "categoryId": c.CategoryID,
        "categoryName": c.CategoryName,
        "type": c.Type,
        "isActive": c.IsActive
    }
    for c in Category.query.order_by(
        Category.IsActive.desc(),
        Category.CategoryName.asc()
    ).all()
])


@admin_bp.route("/categories", methods=["POST"])
@token_required
@roles_required("Admin")
def create_category():
    data = request.get_json(silent=True) or {}
    if not data.get("categoryName"):
        return jsonify({"error": "categoryName is required"}), 400
    c = Category(CategoryName=data["categoryName"], Type=data.get("type", "Enhancement"), IsActive=data.get("isActive", True))
    db.session.add(c)
    db.session.commit()
    return jsonify({"categoryId": c.CategoryID, "categoryName": c.CategoryName}), 201


@admin_bp.route("/categories/<int:category_id>", methods=["PUT"])
@token_required
@roles_required("Admin")
def update_category(category_id):

    print("UPDATE CATEGORY CALLED")   # <-- Add this line

    c = Category.query.get_or_404(category_id)

    data = request.get_json(silent=True) or {}

    c.CategoryName = data.get("categoryName", c.CategoryName)
    c.Type = data.get("type", c.Type)

    db.session.commit()

    return jsonify({
        "categoryId": c.CategoryID,
        "categoryName": c.CategoryName,
        "type": c.Type,
        "isActive": c.IsActive
    })

@admin_bp.route("/categories/<int:category_id>/status", methods=["PUT"])
@token_required
@roles_required("Admin")
def update_category_status(category_id):
    c = Category.query.get_or_404(category_id)
    data = request.get_json(silent=True) or {}
    c.IsActive = bool(data.get("isActive", c.IsActive))
    db.session.commit()
    return jsonify({"categoryId": c.CategoryID, "isActive": c.IsActive})


# ---------------------------------------------------------------- Roles (read-only lookup)
@admin_bp.route("/roles", methods=["GET"])
@token_required
@roles_required("Admin")
def list_roles():
    return jsonify([{"roleId": r.RoleID, "roleName": r.RoleName} for r in Role.query.all()])

# ---------------------------------------------------------------- Business

@admin_bp.route("/business", methods=["GET"])
@token_required
@roles_required("Admin")
def list_business():
    return jsonify([
        {
            "businessId": b.BusinessID,
            "businessName": b.BusinessName,
            "isActive": b.IsActive
        }
        for b in Business.query.order_by(Business.BusinessName).all()
    ])


@admin_bp.route("/business", methods=["POST"])
@token_required
@roles_required("Admin")
def create_business():
    data = request.get_json(silent=True) or {}

    if not data.get("businessName"):
        return jsonify({"error": "businessName is required"}), 400

    if Business.query.filter_by(BusinessName=data["businessName"]).first():
        return jsonify({"error": "Business already exists"}), 409

    b = Business(
        BusinessName=data["businessName"],
        IsActive=data.get("isActive", True)
    )

    db.session.add(b)
    db.session.commit()

    return jsonify(b.to_dict()), 201


@admin_bp.route("/business/<int:business_id>/status", methods=["PUT"])
@token_required
@roles_required("Admin")
def update_business_status(business_id):

    b = Business.query.get_or_404(business_id)

    data = request.get_json(silent=True) or {}

    b.IsActive = bool(data.get("isActive", b.IsActive))

    db.session.commit()

    return jsonify(b.to_dict())
