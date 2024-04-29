from flask import render_template
from app import another_app

@another_app.route('/')
@another_app.route('/index')
def index():
    user = {"username": "Alex"}
    return render_template("baseTemplate.html", user=user)
@another_app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404
@another_app.errorhandler(400)
def error_request(e):
    return render_template("400.html"), 400
