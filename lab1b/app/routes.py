from main import another_app
from flask import request
from flask import make_response
import random

class User:
    def __init__(self, id_user, name):
        self.id = id_user
        self.name = name

def load_user(user_id):
    if user_id == "42":
        return User(42, "Borya")
    elif user_id == "100":
        return User(100, "Sasha")
    else:
        return None

def index():
    user_agent = request.headers.get('User-Agent')
    return '<h1>Hello, your browser is {}</h1>'.format(user_agent)

'''
@another_app.route('/user/<name>')
def hello_user(name):
    return '<h2>Hello, {}<h2>'.format(name)
'''
@another_app.route("/browser")
def browser():
    user_agent = request.headers.get('User-Agent')
    if "Mozilla" in user_agent:
        n = random.randint(100, 1000)
        response = make_response("<h1>Hello, your browser is {}</h1>".format(user_agent))
        response.set_cookie('flag', str(n))
        return response

@another_app.route('/bad_request')
def bad_fill(code=400):
    return '<h3>Bad Request</h3>', code

@another_app.route('/custom_response')
def cust_response():
    response = make_response('<h1>Put this in cookie!<h1>')
    response.set_cookie('answer', '42')
    return response

@another_app.route('/user/<user_id>')
def get_user(user_id):
    user = load_user(user_id)
    if user is None:
        return bad_fill(404)
    else:
        return '<h1>Hello, {}<h1>'.format(user.name)

another_app.add_url_rule("/","index", index)