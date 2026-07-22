import jwt
from functools import wraps
from datetime import datetime, timezone
from flask import request, jsonify, current_app, g
from models import User


def generate_token(user):
    payload = {
        "userId": user.UserID,
        "role": user.role.RoleName,
        "platformId": user.PlatformID,
        "exp": datetime.now(timezone.utc) + current_app.config["JWT_EXPIRY"],
    }
    return jwt.encode(payload, current_app.config["JWT_SECRET_KEY"], algorithm="HS256")


def decode_token(token):
    return jwt.decode(token, current_app.config["JWT_SECRET_KEY"], algorithms=["HS256"])


def token_required(f):
    """Validates the Bearer token and loads the current user onto flask.g"""
    @wraps(f)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Missing or invalid Authorization header"}), 401
        token = auth_header.split(" ", 1)[1]
        try:
            payload = decode_token(token)
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired, please log in again"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401

        user = User.query.get(payload["userId"])
        if not user or user.Status != "Active":
            return jsonify({"error": "User not found or inactive"}), 401

        g.current_user = user
        g.current_role = payload["role"]
        return f(*args, **kwargs)
    return wrapper


def roles_required(*allowed_roles):
    """Use after @token_required. Example: @roles_required('Admin', 'PGC')"""
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if g.current_role not in allowed_roles:
                return jsonify({"error": f"Role '{g.current_role}' is not permitted to perform this action"}), 403
            return f(*args, **kwargs)
        return wrapper
    return decorator
