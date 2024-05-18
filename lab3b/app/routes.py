from flask import render_template, redirect, url_for, session
from app import another_app
from app.forms import SimpleForm

@another_app.route('/')
@another_app.route('/index')
def index():
    default_user = {"username": "Alex"}
    session_text = session.get('text')
    if session_text is not None or session_text != "":
        return render_template("index.html", text=session_text)
    else:
        return render_template("index.html", user=default_user)

@another_app.route('/account')
def account():
    default_user = {"username": "Alex"}
    session_text = session.get('text')
    session_email = session.get('email')
    session_gender = session.get('gender')
    if session_text is not None or session_text != "":
        return render_template("account.html", text=session_text, email=session_email, gender=session_gender)
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
    text = None
    form = SimpleForm()
    if form.validate_on_submit():
        session['text'] = form.text.data
        session['email'] = form.email.data
        session['gender'] = form.gender.data
        form.text.data = ''
        print(session.get('text'))
        return redirect(url_for('index'))
    return render_template('formTemplate.html', form=form, text=text)
