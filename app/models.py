from datetime import datetime
from hashlib import md5

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, login_manager


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


followers = db.Table('followers',
                     db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
                     db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
                     )


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), index=True, unique=True)
    email = db.Column(db.String(60), index=True, unique=True)
    pass_hashed = db.Column(db.String(256))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    followed = db.relationship('User',
                               secondary='followers',
                               primaryjoin=(followers.c.follower_id == id),
                               secondaryjoin=(followers.c.followed_id == id),
                               backref=db.backref('followers', lazy='dynamic'),
                               lazy='dynamic')

    def __repr__(self):
        return 'User <{}:{}>'.format(self.username, self.id)

    def set_password(self, password):
        self.pass_hashed = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.pass_hashed, password)

    def generate_avatar(self, size):
        hash = md5(self.email.lower().encode('utf-8')).hexdigest()
        BASE_URL = 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'
        return BASE_URL.format(hash, size)

    def follower(self, user):
        if not user is self and not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(followers.c.followed_id == user.id).count() > 0

    def generate_post_feed(self):
        others = Post.query.join(
            followers, (followers.c.followed_id == Post.user)
        ).filter(
            (followers.c.follower_id == self.id)
        )
        myself = Post.query.filter_by(id=self.id)
        return others.union(myself).order_by(Post.date.desc())

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(140), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    user = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return 'Post <{}:{}>'.format(self.user, self.date)
