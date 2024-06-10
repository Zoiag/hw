from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView


def setup_admin(app):
    admin = Admin(app, name='Admin Panel', template_mode='bootstrap3')
    from .models import db, User, Product, Cart, CartItem
    admin.add_view(ModelView(User, db.session))
    admin.add_view(ModelView(Product, db.session))
    admin.add_view(ModelView(Cart, db.session))
    admin.add_view(ModelView(CartItem, db.session))