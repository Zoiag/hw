from flask import Flask
from flask_bootstrap import Bootstrap5

another_app = Flask(__name__)
bootstrap = Bootstrap5(another_app)

from app import routes