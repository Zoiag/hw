from flask import render_template, redirect, url_for, session, abort
from . import main
from app.main.forms import SimpleForm
from app.models import User
from flask_mail import Message
from flask_login import login_required
from .. import db

@main.route('/')
@main.route('/index')
def index():
    '''
    default_user = User(email="test@test.com", password="pass", username="test")
    if User.query.filter_by(email=default_user.email).first() is None:
        db.session.add(default_user)
        print(default_user.password_hash)
        db.session.commit()
    '''

    session_text = session.get('text')
    if session_text is not None or session_text != "":
        return render_template("index.html")
    else:
        return render_template("index.html")
    '''
    login = session.get('login')
    email = session.get('email')
    return render_template("index.html", login=login, email=email)
    , auth=session.get('../auth')
    '''

@main.route('/account')
def account():
    default_user = {"username": "Alex"}
    session_login = session.get('login')
    session_email = session.get('email')
    session_gender = session.get('gender')
    if session_login is not None or session_login != "":
        return render_template("account.html", login=session_login, email=session_email, gender=session_gender, auth=session.get(
            '../auth'))
    else:
        return render_template("account.html", user=default_user)

'''
@main.route('/testForm', methods=['GET', 'POST'])
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
    return render_template('formTemplate.html', form=form, auth=session.get('../auth'))

    
@auth.route('/login')
def login():
    return render_template("auth/login.html")    
    

def confirm(user):
    send_mail("ggllzoia@gmail.com", 'Create new user from Flask', 'send_mail', user=user)
    redirect(url_for('index'))
'''

@main.route("/secret")
@login_required
def secret():
    return "Only for auth"


@main.route('/testConfirm')
def testConfirm():
    user = User.query.filter_by().first()
    tmp = user.generate_confirmation_token()
    user.confirm(tmp)
