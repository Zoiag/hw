from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import EqualTo, DataRequired


class SimpleForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    submit = SubmitField('Войти')
