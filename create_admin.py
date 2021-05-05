from application import db
from application.Main.models import Users
from werkzeug.security import generate_password_hash,check_password_hash

admin_user = Users.query.filter_by(is_admin=1)
if admin_user.count() == 0:
    psw = generate_password_hash('theadmin259')
    admin = Users(user_name='admin',profile_pic='admin_profile_pic.png',password=psw,is_admin=1,)
    db.session.add(admin)
    db.session.commit()
else:
    pass