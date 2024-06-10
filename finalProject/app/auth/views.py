from flask import render_template, redirect, request, flash, url_for
from flask_mail import Message
from . import auth
from .forms import LoginForm, RegistrationForm
from .. import db
from ..models import User
from flask_login import login_user, login_required, logout_user, current_user
from threading import Thread
from app import mail


@auth.before_app_request
def before_request():
    """
    Выполняется перед каждым запросом.

    Если пользователь аутентифицирован, обновляет время его последнего визита.
    Если пользователь не подтвердил свой аккаунт, перенаправляет его на страницу неподтвержденного аккаунта,
    за исключением случаев, когда он находится на странице аутентификации или запрашивает статический контент.
    """
    if current_user.is_authenticated:
        current_user.ping()
        if not current_user.confirmed and request.blueprint != 'auth' and request.endpoint != 'static':
            return redirect(url_for('auth.unconfirmed'))


@auth.route('/login', methods=['GET', 'POST'])
def login():
    """
    Маршрут для входа в систему.

    Обрабатывает GET и POST запросы. При GET запросе отображает форму входа.
    При POST запросе проверяет введенные данные, аутентифицирует пользователя и перенаправляет его на нужную страницу.
    Если данные неверны, выводит сообщение об ошибке.
    """
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.password_verify(form.password.data):
            login_user(user, form.remember_me.data)
            next = request.args.get('next')
            if next is None or not next.startswith('/'):
                next = url_for('main.index')
            return redirect(next)
        flash('Invalid username or password')

    return render_template("auth/login.html", form=form)


@auth.route('/register', methods=['GET', 'POST'])
def register():
    """
    Маршрут для регистрации нового пользователя.

    Обрабатывает GET и POST запросы. При GET запросе отображает форму регистрации.
    При POST запросе создает нового пользователя, сохраняет его в базе данных, генерирует токен подтверждения
    и отправляет письмо с подтверждением на указанный email.
    """
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            email=form.email.data,
            username=form.username.data
        )
        user.password = form.password.data
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        send_confirm(user, token)
        return redirect(url_for('auth.login'))
    return render_template("auth/registration.html", form=form)


@auth.route('/logout')
@login_required
def logout():
    """
    Маршрут для выхода из системы.

    Выполняет выход пользователя из системы и перенаправляет его на главную страницу с уведомлением.
    """
    logout_user()
    flash('Вы вышли из системы')
    return redirect(url_for('main.index'))


@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    """
    Маршрут для подтверждения аккаунта.

    Обрабатывает GET запрос с токеном подтверждения. Если пользователь уже подтвержден, перенаправляет на главную страницу.
    В противном случае проверяет токен и, если он валиден, подтверждает аккаунт пользователя и сохраняет изменения в базе данных.
    Выводит соответствующее сообщение о результате подтверждения.
    """
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token.encode('utf-8')):
        db.session.commit()
        flash("Ваше подтверждение прошло успешно, спасибо!")
    else:
        flash("Ваша ссылка не валидна или истекла")
    return redirect(url_for('main.index'))


@auth.route('/unconfirmed')
def unconfirmed():
    """
    Маршрут для отображения страницы неподтвержденного аккаунта.

    Если текущий пользователь анонимный или уже подтвердил свой аккаунт, перенаправляет на главную страницу.
    В противном случае отображает страницу с уведомлением о неподтвержденном аккаунте.
    """
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')


def send_confirm(user, token):
    """
    Отправляет email с подтверждением аккаунта.

    Генерирует письмо с токеном подтверждения и отправляет его на email пользователя.
    После отправки перенаправляет на главную страницу.
    """
    send_mail(user.email, 'Подтвердите свой аккаунт', "auth/confirm", user=user, token=token.decode('utf-8'))
    redirect(url_for('main.index'))


def send_mail(to, subject, template, **kwargs):
    """
    Отправляет email.

    Создает объект сообщения с указанным получателем, темой и шаблоном.
    Запускает отправку письма в отдельном потоке.
    """
    msg = Message(subject, sender="student1imo327@gmail.com", recipients=[to])
    try:
        msg.html = render_template(template + ".html", **kwargs)
    except:
        msg.body = render_template(template + ".txt", **kwargs)
    from main import another_app
    thread = Thread(target=send_async_email, args=[another_app, msg])
    thread.start()
    return thread


def send_async_email(app, msg):
    """
    Асинхронная отправка email.

    Обеспечивает отправку email в фоновом режиме для предотвращения блокировки основного потока выполнения приложения.
    """
    with app.app_context():
        mail.send(msg)
