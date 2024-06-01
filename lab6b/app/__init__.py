from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from flask_bootstrap import Bootstrap5
from flask_mail import Mail
from config import config


bootstrap = Bootstrap5()
db = SQLAlchemy()
mail = Mail()

def create_app(config_name="default"):
    another_app = Flask(__name__)
    another_app.config.from_object(config[config_name])
    config[config_name].init_app(another_app)

    bootstrap.init_app(another_app)
    mail.init_app(another_app)
    db.init_app(another_app)

    from .main import main as main_blueprint
    another_app.register_blueprint(main_blueprint)


    return another_app


