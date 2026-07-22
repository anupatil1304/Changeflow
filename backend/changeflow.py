# import os
# from flask import Flask, jsonify, request, send_from_directory
# from sqlalchemy import text
# from config import Config
# from extensions import db, cors

# FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))


# def ensure_master_columns(app):
#     with app.app_context():
#         for table_name, column_name in [("ChangeFlowPlatforms", "IsActive"), ("ChangeFlowCategories", "IsActive")]:
#             existing = db.session.execute(
#                 text(f"SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{table_name}' AND COLUMN_NAME = '{column_name}'")
#             ).fetchone()
#             if existing:
#                 continue
#             if table_name == "ChangeFlowPlatforms":
#                 db.session.execute(text("ALTER TABLE dbo.ChangeFlowPlatforms ADD IsActive BIT NOT NULL CONSTRAINT DF_Platforms_IsActive DEFAULT 1"))
#             else:
#                 db.session.execute(text("ALTER TABLE dbo.ChangeFlowCategories ADD IsActive BIT NOT NULL CONSTRAINT DF_Categories_IsActive DEFAULT 1"))
#         db.session.commit()


# def create_app():
#     app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path="")
#     app.config.from_object(Config)

#     db.init_app(app)
#     app.config["CORS_HEADERS"] = "Content-Type"
#     cors.init_app(app, resources={r"/api/*": {"origins": app.config["CORS_ORIGINS"]}}, supports_credentials=True)

#     from routes.auth import auth_bp
#     from routes.requests import requests_bp
#     from routes.approvals import approvals_bp
#     from routes.development import development_bp
#     from routes.dashboard import dashboard_bp
#     from routes.admin import admin_bp
#     from routes.reports import reports_bp
#     from routes.lookups import lookups_bp

#     app.register_blueprint(auth_bp)
#     app.register_blueprint(requests_bp)
#     app.register_blueprint(approvals_bp)
#     app.register_blueprint(development_bp)
#     app.register_blueprint(dashboard_bp)
#     app.register_blueprint(admin_bp)
#     app.register_blueprint(reports_bp)
#     app.register_blueprint(lookups_bp)
#     ensure_master_columns(app)

#     @app.route("/api/health")
#     def health():
#         return jsonify({"status": "ok"})
    


#     @app.route("/uploads/<path:filename>")
#     def uploaded_file(filename):
#         return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

#     @app.after_request
#     def add_cors_headers(response):
#         if request.path.startswith("/api/"):
#             origin = app.config.get("CORS_ORIGINS", "*")
#             if isinstance(origin, (list, tuple)):
#                 origin = ", ".join(origin)
#             response.headers.setdefault("Access-Control-Allow-Origin", origin)
#             response.headers.setdefault("Access-Control-Allow-Credentials", "true")
#             response.headers.setdefault("Access-Control-Allow-Headers", "Authorization,Content-Type")
#             response.headers.setdefault(
#                 "Access-Control-Allow-Methods",
#                 "GET,POST,PUT,PATCH,DELETE,OPTIONS,HEAD",
#             )
#         return response

#     @app.errorhandler(404)
#     def not_found(e):
#         if request.path.startswith("/api/"):
#             return jsonify({"error": "Not found"}), 404
#         return app.send_static_file("index.html")

#     # @app.errorhandler(500)
#     # def server_error(e):
#     #     return jsonify({"error": "Internal server error"}), 500

#     @app.errorhandler(500)
#     def server_error(e):
#         raise e

#     return app


# if __name__ == "__main__":
#     app = create_app()
#     with app.app_context():
#         # db.create_all()
#         ensure_master_columns(app)
#     app.run(host="0.0.0.0", port=9696, debug=False)





import os
from flask import Flask, jsonify, request, send_from_directory
from sqlalchemy import text
from config import Config
from extensions import db, cors

FRONTEND_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "frontend")
)


def ensure_master_columns(app):
    with app.app_context():
        for table_name, column_name in [
            ("ChangeFlowPlatforms", "IsActive"),
            ("ChangeFlowCategories", "IsActive"),
        ]:

            existing = db.session.execute(
                text(
                    f"""
                    SELECT 1
                    FROM INFORMATION_SCHEMA.COLUMNS
                    WHERE TABLE_NAME = '{table_name}'
                    AND COLUMN_NAME = '{column_name}'
                    """
                )
            ).fetchone()

            if existing:
                continue

            if table_name == "ChangeFlowPlatforms":
                db.session.execute(
                    text(
                        """
                        ALTER TABLE dbo.ChangeFlowPlatforms
                        ADD IsActive BIT NOT NULL
                        CONSTRAINT DF_Platforms_IsActive DEFAULT 1
                        """
                    )
                )
            else:
                db.session.execute(
                    text(
                        """
                        ALTER TABLE dbo.ChangeFlowCategories
                        ADD IsActive BIT NOT NULL
                        CONSTRAINT DF_Categories_IsActive DEFAULT 1
                        """
                    )
                )

        db.session.commit()


def create_app():
    app = Flask(
        __name__,
        static_folder=FRONTEND_DIR,
        static_url_path=""
    )

    app.config.from_object(Config)

    print("===================================")
    print("CORS_ORIGINS =", app.config.get("CORS_ORIGINS"))
    print("===================================")

    db.init_app(app)

    app.config["CORS_HEADERS"] = "Content-Type"

    # Allow all origins temporarily for testing
    cors.init_app(
        app,
        resources={r"/*": {"origins": "*"}},
        supports_credentials=True
    )


    from routes.auth import auth_bp
    from routes.requests import requests_bp
    from routes.approvals import approvals_bp
    from routes.development import development_bp
    from routes.dashboard import dashboard_bp
    from routes.admin import admin_bp
    from routes.reports import reports_bp
    from routes.lookups import lookups_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(requests_bp)
    app.register_blueprint(approvals_bp)
    app.register_blueprint(development_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(lookups_bp)

    ensure_master_columns(app)

    @app.route("/api/health")
    def health():
        return jsonify({"status": "ok"})

    @app.route("/uploads/<path:filename>")
    def uploaded_file(filename):
        return send_from_directory(
            app.config["UPLOAD_FOLDER"],
            filename
        )

    @app.errorhandler(404)
    def not_found(e):
        if request.path.startswith("/api/"):
            return jsonify({"error": "Not found"}), 404

        return app.send_static_file("index.html")

    @app.errorhandler(500)
    def server_error(e):
        raise e

    return app


if __name__ == "__main__":
    app = create_app()

    with app.app_context():
        ensure_master_columns(app)

    app.run(
        host="0.0.0.0",
        port=9696,
        debug=False
    )

