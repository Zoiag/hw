from flask import render_template
from . import main

@main.errorhandler(404)
def page_not_found(e):
    return render_template("errors/404.html"), 404
@main.errorhandler(400)
def error_request(e):
    return render_template("errors/400.html"), 400