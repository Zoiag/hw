from flask_login import UserMixin

from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from . import login_manager
from authlib.jose import jwt
from authlib.jose import JsonWebSignature


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), unique=True)
    users = db.relationship('User', backref='role')

    def __repr__(self):
        return '<Role %r>' % self.name


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(60), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    email = db.Column(db.String(64), unique=True, nullable=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    confirmed = db.Column(db.Boolean, default=False)


    def generate_confirmation_token(self):
        jws = JsonWebSignature()
        protected = {'alg': 'HS256'}
        payload = self.id
        secret = 'secret'
        return jws.serialize_compact(protected, payload, secret)

    def confirm(self, token):
        jws = JsonWebSignature()
        data = jws.deserialize_compact(s=token, key='secret')
        if data.payload.decode('utf-8') != str(self.id):
            print('Invalid confirmation token')
            return False
        else:
            self.confirmed = True
            db.session.add(self)
            return True


    @property
    def password(self):
        raise AttributeError('password not enable for read')


    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')

    def password_verify(self, password):
        return check_password_hash(self.password_hash, password)


    def __repr__(self):
        return '<User %r>' % self.username

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
