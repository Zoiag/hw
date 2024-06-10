from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length, Regexp, EqualTo, ValidationError

from app.models import User


class LoginForm(FlaskForm):
    email = StringField('Почта', validators=[DataRequired(), Length(1, 64), Email()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class RegistrationForm(FlaskForm):
    email = StringField('Почта', validators=[DataRequired(), Length(1, 64), Email()])
    username = StringField('Логин', validators=[DataRequired(), Length(1, 64),
                                                Regexp('^[A-Za-z][A-Za-z0-9_.]*$',
                                                       0, 'Логин должен содержать только буквы, '
                                                          'цифры точки и нижние подчеркивания')])
    password = PasswordField('Пароль', validators=[DataRequired(), EqualTo('password2',
                                                                           message='Пароли должны совпадать')])
    password2 = PasswordField('Повторите пароль', validators=[DataRequired()])
    submit = SubmitField('Зарегистрироваться')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Почта уже зарегистрирована')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Логин уже занят')

