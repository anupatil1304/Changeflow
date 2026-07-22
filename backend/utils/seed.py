"""
Run once to initialize the database with tables + sample data that has
working (hashed) passwords, so you can log in immediately.

    cd backend
    python utils/seed.py

Sample logins (password for all: Passw0rd!):
    admin@demo.com          -> Admin
    requester@demo.com      -> Requester
    platformowner@demo.com  -> Platform Owner
    pgc@demo.com            -> PGC
    developer@demo.com      -> Developer
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from werkzeug.security import generate_password_hash
from backend.changeflow import create_app
from extensions import db
from models import Role, Platform, User, Category, Business

app = create_app()

with app.app_context():
    db.create_all()

    if Role.query.count() == 0:
        roles = [Role(RoleName=n) for n in
                  ["Requester", "Platform Owner", "PGC", "Developer", "Admin"]]
        db.session.add_all(roles)
        db.session.commit()

    if Business.query.count() == 0:
        db.session.add_all([
            Business(BusinessName="Retail"),
            Business(BusinessName="Jio"),
            Business(BusinessName="New Energy"),
            Business(BusinessName="Jamnagar"),
            Business(BusinessName="RCP"),
            Business(BusinessName="Other MFG"),
        ])
        db.session.commit()

    if Platform.query.count() == 0:
        platforms = [Platform(PlatformName=n) for n in
                      ["Core Banking Platform", "Customer Mobile App", "Internal HR Portal"]]
        db.session.add_all(platforms)
        db.session.commit()

    if Category.query.count() == 0:
        db.session.add_all([
            Category(CategoryName="New Feature", Type="Enhancement"),
            Category(CategoryName="Bug Fix", Type="Enhancement"),
            Category(CategoryName="New Project", Type="Project"),
            Category(CategoryName="Integration", Type="Enhancement"),
        ])
        db.session.commit()

    if User.query.count() == 0:
        role_map = {r.RoleName: r.RoleID for r in Role.query.all()}
        platform_id = Platform.query.first().PlatformID
        pwd = generate_password_hash("Passw0rd!")

        users = [
            User(Name="Alice Admin", Email="admin@demo.com", PasswordHash=pwd,
                 RoleID=role_map["Admin"], PlatformID=None),
            User(Name="Ravi Requester", Email="requester@demo.com", PasswordHash=pwd,
                 RoleID=role_map["Requester"], PlatformID=platform_id),
            User(Name="Priya Owner", Email="platformowner@demo.com", PasswordHash=pwd,
                 RoleID=role_map["Platform Owner"], PlatformID=platform_id),
            User(Name="George PGC", Email="pgc@demo.com", PasswordHash=pwd,
                 RoleID=role_map["PGC"], PlatformID=None),
            User(Name="Dev Kumar", Email="developer@demo.com", PasswordHash=pwd,
                 RoleID=role_map["Developer"], PlatformID=platform_id),
        ]
        db.session.add_all(users)
        db.session.commit()

        # Make Priya Owner the OwnerID for the first platform
        platform = Platform.query.first()
        platform.OwnerID = User.query.filter_by(Email="platformowner@demo.com").first().UserID
        db.session.commit()

    print("Database seeded. Sample users created with password: Passw0rd!")
