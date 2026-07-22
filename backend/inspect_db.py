from backend.changeflow import create_app
from models import User
app = create_app()
with app.app_context():
    rows = User.query.all()
    print('users', len(rows))
    for u in rows:
        print(u.Email, '|', u.Name, '|', u.Status, '|', u.PasswordHash[:120])
