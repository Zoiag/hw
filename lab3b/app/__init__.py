from flask import Flask
from flask_bootstrap import Bootstrap5

another_app = Flask(__name__)
another_app.config['SECRET_KEY'] = 'hard to unlock'
bootstrap = Bootstrap5(another_app)

#from app import routes
