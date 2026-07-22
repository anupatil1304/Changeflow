from flask import Blueprint, request, jsonify, g
from werkzeug.security import check_password_hash
from extensions import db
from models import User
from utils.decorators import generate_token, token_required

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    user = User.query.filter(db.func.lower(User.Email) == email).first()
    if not user or not check_password_hash(user.PasswordHash, password):
        return jsonify({"error": "Invalid email or password"}), 401
    if user.Status != "Active":
        return jsonify({"error": "This account is inactive. Contact an administrator."}), 403

    token = generate_token(user)
    return jsonify({"token": token, "user": user.to_dict()})


@auth_bp.route("/forgot-password", methods=["POST"])
def forgot_password():
    """
    Stub endpoint matching the 'Forgot Password' control on the Login screen.
    In production this should generate a time-limited reset token and email it.
    """
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    user = User.query.filter(db.func.lower(User.Email) == email).first()
    # Always return 200 (don't reveal whether the email exists)
    if user:
        # TODO: generate reset token + send email
        pass
    return jsonify({"message": "If that email exists, password reset instructions have been sent."})


@auth_bp.route("/me", methods=["GET"])
@token_required
def me():
    return jsonify(g.current_user.to_dict())
