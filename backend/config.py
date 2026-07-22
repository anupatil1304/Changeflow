# """
# Application configuration.
# """

# import os
# from datetime import timedelta
# from urllib.parse import quote_plus

# BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# # ODBC connection string for SQL Server LocalDB
# params = quote_plus(
#     "DRIVER={ODBC Driver 18 for SQL Server};"
#     "SERVER=10.131.88.53;"
#     "DATABASE=kiosk;"
#     "Trusted_Connection=yes;"
#     "TrustServerCertificate=yes;"
# )


# class Config:
#     SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-me")
#     JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "dev-jwt-secret-change-me")
#     JWT_EXPIRY = timedelta(hours=8)

#     SQLALCHEMY_DATABASE_URI = (
#         f"mssql+pyodbc:///?odbc_connect={params}"
#     )

#     SQLALCHEMY_TRACK_MODIFICATIONS = False

#     UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
#     MAX_CONTENT_LENGTH = 2 * 1024 * 1024

#     CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "*")




"""
Application configuration.
"""

import os
from datetime import timedelta
from urllib.parse import quote_plus

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# ODBC connection string for SQL Server
params = quote_plus(
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=10.131.88.53;"
    "DATABASE=kiosk;"
    "UID=antuser;"
    "PWD=User@123;"
    "TrustServerCertificate=yes;"
)


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-me")
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "dev-jwt-secret-change-me")
    JWT_EXPIRY = timedelta(hours=8)

    SQLALCHEMY_DATABASE_URI = (
        f"mssql+pyodbc:///?odbc_connect={params}"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
    MAX_CONTENT_LENGTH = 2 * 1024 * 1024

    CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "*")