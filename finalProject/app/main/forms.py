from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.fields.choices import SelectField
from wtforms.fields.numeric import FloatField
from wtforms.fields.simple import TextAreaField, BooleanField
from wtforms.validators import DataRequired, Length
from flask_wtf.file import FileField, FileAllowed
from wtforms import HiddenField
from app.models import Role, User


class SimpleForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    submit = SubmitField('Войти')


class ProductForm(FlaskForm):
    name = StringField('Название', validators=[DataRequired(), Length(min=1, max=64)])
    description = TextAreaField('Описание', validators=[DataRequired()])
    price = FloatField('Цена', validators=[DataRequired()])
    image = FileField('Изображение продукта', validators=[FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')])
    author = StringField('Автор', validators=[DataRequired()])  # Добавляем поле автора
    submit = SubmitField('Сохранить')

    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        self.author.choices = [(user.id, user.username) for user in User.query.order_by(User.username).all()]


class OrderForm(FlaskForm):
    name = StringField('Имя и Фамилия', validators=[DataRequired(), Length(min=2, max=50)])
    phone = StringField('Телефон', validators=[DataRequired(), Length(min=10, max=15)])
    address = StringField('Адрес доставки или самовывоз', validators=[DataRequired(), Length(min=10, max=100)])
    comment = TextAreaField('Комментарий к заказу', validators=[Length(max=200)])
    agree = BooleanField('Согласие на обработку персональных данных', validators=[DataRequired()])
    submit = SubmitField('Оформить заказ')


class OrderStatusForm(FlaskForm):
    status = SelectField('Статус', choices=[
        ('Ожидает звонка/сообщения', 'Ожидает звонка/сообщения'),
        ('Ожидаем оплаты', 'Ожидаем оплаты'),
        ('Не отправлено', 'Не отправлено'),
        ('Отправлено', 'Отправлено'),
        ('Ожидает самовывоза', 'Ожидает самовывоза'),
        ('Товар у заказчика', 'Товар у заказчика')
    ])
    submit = SubmitField('Изменить статус')


class ReviewForm(FlaskForm):
    content = StringField('Отзыв', validators=[DataRequired()])
    submit = SubmitField('Оставить отзыв')


class RoleForm(FlaskForm):
    role = SelectField('Роль', coerce=int)
    submit = SubmitField('Изменить')

    def __init__(self, *args, **kwargs):
        super(RoleForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name) for role in Role.query.order_by(Role.name).all()]


class SaveProductForm(FlaskForm):
    csrf_token = HiddenField()
