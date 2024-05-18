from flask_wtf import FlaskForm
from wtforms import *
from wtforms.validators import EqualTo, Length, Email, Regexp, input_required


class SimpleForm(FlaskForm):
    email = StringField('Email', validators=[input_required(),
                                                 Length(1, 64), Email()])
    text = StringField('Логин', validators=[input_required(),
                                                       Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                                              'Логин должен иметь только буквы, цифры'
                                                              'нижнее подчеркивание или точку')])
    password = PasswordField('Пароль', validators=[input_required(),
                                                     EqualTo('password2',
                                                             message="Пароль должен совпадать")])
    password2 = PasswordField('Повторите пароль', validators=[input_required()])
    gender = SelectField('Пол', choices=[('жен', 'Женский'), ('муж', 'Мужской')])
    submit = SubmitField('Регистрация')