from application import db,app
from flask import Flask,request,Blueprint,jsonify
from application.Main.models import Users,UsersSchema,Messages,MessagesSchema,Notification,NotificationsSchema,MutedUsers,MetedUserSchema
from werkzeug.security import generate_password_hash,check_password_hash

import os
from sqlalchemy import text
from datetime import datetime
from werkzeug.utils import secure_filename

main = Blueprint('main', __name__,static_folder='../static')

def remove_file(file, type):
    file_name = file
    folder = os.path.join(app.root_path, "static/" + type + "/"+file_name)
    os.remove(folder)
    return 'File Has Been Removed'


def save_file(file, type):
    file_name = secure_filename(file.filename)
    file_ext = file_name.split(".")[1]
    folder = os.path.join(app.root_path, "static/" + type + "/")
    file_path = os.path.join(folder, file_name)
    try:
        file.save(file_path)
        return True, file_name
    except:
        return False, file_name


@main.route('/register_user',methods=['POST'])
def Register():
    user_name = request.form.get('user_name')
    password = request.form.get('password')
    profile_pic = request.files.get('profile_pic')
    hash_password = generate_password_hash(password)
    print(profile_pic.filename)
    check_username_exist = Users.query.filter_by(user_name=user_name).first()

    if check_username_exist:
        return jsonify({'msg':'User Name Already Exist.Please Try Another One'})
    else:
        user = Users(user_name=user_name,password=hash_password,profile_pic=profile_pic.filename,is_admin=0)
        save_file(profile_pic,'profile_pics')
        db.session.add(user)
        db.session.commit()
        return jsonify({'msg':'You are Successfully Registered'})


@main.route('/login_user',methods=['POST'])
def Login():
    user_name = request.form.get('user_name')
    password = request.form.get('password')

    user = Users.query.filter_by(user_name=user_name).first()

    if user and check_password_hash(user.password,password):
        user_schema = UsersSchema()
        user_info = user_schema.dump(user)
        return jsonify({'msg':'You are Successfully Logged In','user':user_info})
    else:
        return jsonify({'msg':'Incorrect Username or Password. Please Try Again'})
    


@main.route('/get_all_users')
def GetAllUsers():
    want_to_search = request.args.get('want_to_search')
    if want_to_search == 'true':
        searched_user = request.args.get('searched_user')
        search_sql = text("SELECT *,(select count(*) from muted_users where muted_user_id=user_id) as is_muted FROM users WHERE is_admin=0 AND user_name LIKE'%"+str(searched_user)+"%'")
        search_query = db.engine.execute(search_sql)
        users_schema = UsersSchema(many=True)
        all_users = users_schema.dump(search_query)
        return jsonify({'all_users':all_users})
    else:
        get_users_sql = text("SELECT *,(select count(*) from muted_users where muted_user_id=user_id) as is_muted FROM users WHERE is_admin=0")
        get_user_query = db.engine.execute(get_users_sql)
        users_schema = UsersSchema(many=True)
        all_users = users_schema.dump(get_user_query)

        
        return jsonify({'all_users':all_users})


@main.route('/check_group_mutation')
def CheckMutation():
    user_id = request.args.get('user_id')
    check_mutation =  MutedUsers.query.filter_by(muted_user_id=user_id).first()
    
    if check_mutation:
        return jsonify({'msg':'Sorry you are muted you cannot chat with the group'})
    else:
        return jsonify({'msg':'You can do chat with the group'})



@main.route('/get_user_info')
def GetUserInfo():
    user_id = request.args.get('user_id')
    user = Users.query.filter_by(user_id=user_id).first()
    user_schema = UsersSchema()
    user_info = user_schema.dump(user)

    
    return jsonify({'user':user_info})


@main.route('/mute_user')
def MuteUser():
    user_id = request.args.get('user_id')
    muted_user= MutedUsers.query.filter_by(muted_user_id=user_id).first()
    if muted_user:
        db.session.delete(muted_user)
        db.session.commit()
        return jsonify({'msg':'the user has been unmuted'})
    else:
        user = MutedUsers(muted_user_id=user_id)
        db.session.add(user)
        db.session.commit()
        return jsonify({'msg':'the user has been muted'})


@main.route('/get_subscribers')
def GetSubscribers():
    get_muted_users_count = MutedUsers.query.count()
    get_all_users_count = Users.query.count()

    
    return jsonify({'subscribers':get_all_users_count - get_muted_users_count})





@main.route('/insert_msg',methods=['POST'])
def InsertMsg():
    image = request.files.get('image')
    msg_txt = request.form.get('msg')
    emoji = request.form.get('emoji')
    inserted_by = request.form.get('inserted_by')

    if image:
        save_file(image,'msg_images')
        msg = Messages(sended_by=inserted_by,message_txt=msg_txt,emoji=emoji,image=image.filename)

    else:
        msg = Messages(sended_by=inserted_by,message_txt=msg_txt,emoji=emoji,image=image)

    db.session.add(msg)
    db.session.commit()
    return jsonify({'msg':'Message has been inserted'})

@main.route('/get_msgs')
def GetMsgs():
    get_msgs_sql = text("SELECT *,(select count(*) from muted_users where muted_user_id=sended_by) as muted  from messages LEFT join users on users.user_id=sended_by")
    get_msg_query = db.engine.execute(get_msgs_sql)
    msgs_schema = MessagesSchema(many=True)
    msgs = msgs_schema.dump(get_msg_query)
    return jsonify({'msgs':msgs})


@main.route('/insert_notifications', methods=['POST'])
def InsertNotification():
    notification_txt = request.form.get('notification_txt')
    create_by = request.form.get('created_by')
    all_users = Users.query.filter(Users.user_id != create_by).all()
    for user in all_users:
        notification = Notification(created_by=create_by,notification_txt=notification_txt,seen=0,reciever=user.user_id)
        db.session.add(notification)
        db.session.commit()

    return jsonify({'msg':'Notification has been added'})

@main.route('/get_notifications')
def GetNotifications():
    my_id = request.args.get('my_id')
    notifications_sql =  text("SELECT * from notification LEFT join users on user_id=reciever where reciever="+str(my_id))
    notifications_query = db.engine.execute(notifications_sql)
    notifications_schema = NotificationsSchema(many=True)
    notifications = notifications_schema.dump(notifications_query)

    notification_count = Notification.query.filter_by(seen=0,reciever=my_id)
    
    return jsonify({'notifications':notifications,'notifications_count':notification_count.count()})

   
    
@main.route('/seen_all_notifications')
def seen_all_notifications():
    my_id = request.args.get('my_id')
    check_existance = Notification.query.filter_by(seen=0,reciever=my_id)
    if check_existance.count() >0:
        check = Notification.query.filter_by(seen=0,reciever=my_id).all()
        for seen in check:
            
            seen.seen = 1
            db.session.commit()
            
    else:
        return jsonify({'msg':'No Notifications'})

    return jsonify({'msg':'checked'})





@main.route('/delete_notification')
def DeleteNotification():
    id = request.args.get('id')
    notification = Notification.query.filter_by(notification_id=id).first()
    db.session.delete(notification)
    db.session.commit()
    return jsonify({'msg':'Notifcation has Been deleted'})


    

