from backend.changeflow import create_app
from models import User
from werkzeug.security import check_password_hash
app = create_app()
candidates = ['Password123!','Password123','password123!','Password1!','Password12345','Welcome123!','Welcome123','Demo123!','demo123!','Admin123!','admin123!','P@ssw0rd!','P@ssword123','ChangeFlow123!','ChangeFlow2026!','ChangeFlow!','123456','password','Password!','Test123!','test123!','Admin@123','Admin123','Pass@123','Pass123!','Password@123','Password@123!','Welcome@123!','Welcome@123','P@ssword1!']
with app.app_context():
    for u in User.query.all():
        print('user', u.Email)
        for pwd in candidates:
            try:
                ok = check_password_hash(u.PasswordHash, pwd)
            except Exception as e:
                ok = f'ERR:{e}'
            if ok:
                print(' matched', pwd)
                break
        else:
            print(' no candidate matched')
