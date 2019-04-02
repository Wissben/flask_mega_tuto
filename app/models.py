from app import db,login_manager
from datetime import datetime
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import UserMixin
from hashlib import md5
from flask import abort

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


class User(UserMixin,db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), index=True, unique=True)
    email = db.Column(db.String(60), index=True, unique=True)
    pass_hashed = db.Column(db.String(256))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime,default=datetime.utcnow)

    def __repr__(self):
        return 'User <{}:{}>'.format(self.username, self.id)

    def set_password(self,password):
        self.pass_hashed = generate_password_hash(password)

    def check_password(self,password):
        return check_password_hash(self.pass_hashed,password)

    def generate_avatar(self,size):
        hash = md5(self.email.lower().encode('utf-8')).hexdigest()
        BASE_URL = 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'
        return BASE_URL.format(hash,size)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(140), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    user = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return 'Post <{}:{}>'.format(self.user, self.date)
