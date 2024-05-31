import os
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from flask_bootstrap import Bootstrap5
from flask_migrate import Migrate
from flask_mail import Mail

basedir = os.path.abspath(os.path.dirname(__file__))

another_app = Flask(__name__)

another_app.config['SECRET_KEY'] = 'hard to unlock'
another_app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/flask_education'
another_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

another_app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
another_app.config['MAIL_PORT'] = 587
another_app.config['MAIL_USE_TLS'] = True
another_app.config['MAIL_USERNAME'] = "student1imo327@gmail.com"
another_app.config['MAIL_PASSWORD'] = "liqq gqyp nenp jfwa"


bootstrap = Bootstrap5(another_app)
db = SQLAlchemy(another_app)
mail = Mail(another_app)

from models import *
migrate = Migrate(another_app, db)

#from app import routes

