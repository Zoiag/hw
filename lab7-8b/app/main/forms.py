from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import EqualTo, DataRequired


class SimpleForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired(), EqualTo('password2', message="Пароль должен совпадать")])
    password2 = PasswordField('Повторите пароль', validators=[DataRequired()])
    email = StringField('Почта', validators=[DataRequired()])

    submit = SubmitField('Войти')
