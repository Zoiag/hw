from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask import Flask
from flask_bootstrap import Bootstrap5
from flask_mail import Mail
from config import config
from authlib.integrations.flask_client import OAuth
from flask_migrate import Migrate


bootstrap = Bootstrap5()
db = SQLAlchemy()
mail = Mail()
oauth = OAuth()
login_manager = LoginManager()
migrate = Migrate()
login_manager.login_view = 'auth.login'


def create_app(config_name="default"):
    another_app = Flask(__name__)
    another_app.config.from_object(config[config_name])
    config[config_name].init_app(another_app)

    login_manager.init_app(another_app)
    bootstrap.init_app(another_app)
    mail.init_app(another_app)
    db.init_app(another_app)
    migrate.init_app(another_app, db)
    oauth.init_app(another_app)
    from .main import main as main_blueprint
    another_app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    another_app.register_blueprint(auth_blueprint, url_prefix="/auth")

    return another_app


