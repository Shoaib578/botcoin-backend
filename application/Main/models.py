from application import db
from marshmallow_sqlalchemy import ModelSchema

class Users(db.Model):
    user_id = db.Column(db.Integer,primary_key=True)
    user_name = db.Column(db.String(100),unique=True,nullable=False)
    password = db.Column(db.String(200),nullable=False)
    profile_pic = db.Column(db.String(200))
    is_admin = db.Column(db.Integer(),nullable=False)

class UsersSchema(ModelSchema):
    class Meta:
        fields = ('user_id','user_name','password','profile_pic','is_muted','is_admin')


class MutedUsers(db.Model):
    muted_id = db.Column(db.Integer(), primary_key=True)
    muted_user_id = db.Column(db.Integer(), db.ForeignKey('users.user_id'))
class MetedUserSchema(ModelSchema):
    class Meta:
        fields = ('muted_id','muted_user_id','is_muted')

class Messages(db.Model):
    message_id = db.Column(db.Integer(), primary_key=True)
    sended_by = db.Column(db.Integer,db.ForeignKey('users.user_id'))
    message_txt = db.Column(db.String(500))
    image = db.Column(db.String(200))
    emoji = db.Column(db.String(100))
    

class MessagesSchema(ModelSchema):
    class Meta:
        fields = ('user_id','message_id','sended_by','message_txt','image','emoji','muted','profile_pic','user_name')





class Notification(db.Model):
    notification_id = db.Column(db.Integer(),primary_key=True)
    notification_txt = db.Column(db.String(100))
    created_by = db.Column(db.Integer,db.ForeignKey('users.user_id'))
    reciever = db.Column(db.Integer())
    seen = db.Column(db.Integer())


class NotificationsSchema(ModelSchema):
    class Meta:
        fields = ('user_id','notification_id','notification_txt','created_by','seen','reciever','notification_count','profile_pic','user_name')