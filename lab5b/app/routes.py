from urllib import request

from flask import render_template, redirect, url_for, session
from app import another_app
from app.forms import SimpleForm
from models import User
from flask_mail import Message
from . import mail
import os.path

@another_app.route('/')
@another_app.route('/index')
def index():
    '''
        default_user = {"username": "Alex"}
        session_text = session.get('text')
        if session_text is not None or session_text != "":
            return render_template("index.html", text=session_text, auth=session.get('auth'))
        else:
            return render_template("index.html", user=default_user, auth=session.get('auth'))
    '''
    login = session.get('login')
    email = session.get('email')
    return render_template("index.html", login=login, email=email, auth=session.get('auth'))


@another_app.route('/account')
def account():
    default_user = {"username": "Alex"}
    session_login = session.get('login')
    session_email = session.get('email')
    session_gender = session.get('gender')
    if session_login is not None or session_login != "":
        return render_template("account.html", login=session_login, email=session_email, gender=session_gender, auth=session.get('../auth'))
    else:
        return render_template("account.html", user=default_user)

@another_app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404
@another_app.errorhandler(400)
def error_request(e):
    return render_template("400.html"), 400

@another_app.route('/testForm', methods=['GET', 'POST'])
def testForm():
    form = SimpleForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is not None:
            if user.password == form.password.data:
                session['auth'] = True
                session['login'] = user.username
                session['email'] = user.email
            else:
                session['auth'] = False
                session['login'] = None
                session['email'] = None
        else:
            session['auth'] = False
            session['login'] = None
            session['email'] = None
        confirm(user)
        return redirect(url_for('index'))
    return render_template('formTemplate.html', form=form, auth=session.get('auth'))

@another_app.route('/logout')
def logout():
    if session.get('auth'):
        session['auth'] = False
        session['login'] = None
        session['email'] = None
    return redirect(url_for('index'))
def confirm(user):
    send_mail("ggllzoia@gmail.com", 'Create new user from Flask', 'send_mail', user=user)
    return redirect(url_for('index'))

def send_mail(to, subject, template, **kwargs):
    msg = Message(subject,
                  sender=another_app.config['MAIL_USERNAME'],
                  recipients=[to])
    msg.html = render_template(template + ".html", **kwargs)
    msg.body = render_template(template + ".txt", **kwargs)

    mail.send(msg)
