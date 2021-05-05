from flask import Flask,Blueprint,jsonify,request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os


app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] =os.environ.get('DATABASE_URL').replace('postgres://', 'postgresql://')

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
Migrate(app,db)
from application.Main.routes import main
app.register_blueprint(main)
