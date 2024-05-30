import os
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from flask_bootstrap import Bootstrap5
from flask_migrate import Migrate

basedir = os.path.abspath(os.path.dirname(__file__))

another_app = Flask(__name__)

another_app.config['SECRET_KEY'] = 'hard to unlock'
another_app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/flask_education'
another_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

bootstrap = Bootstrap5(another_app)
db = SQLAlchemy(another_app)

from models import *
migrate = Migrate(another_app, db)

#from app import routes

