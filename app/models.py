from datetime import datetime
from hashlib import md5
from time import time

import jwt
from flask import current_app
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app import db, login_manager
from app.search import add_to_index, query_index, remove_from_index


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


followers = db.Table('followers',
                     db.Column('follower_id', db.Integer,
                               db.ForeignKey('user.id')),
                     db.Column('followed_id', db.Integer,
                               db.ForeignKey('user.id'))
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

    def follow(self, user):
        if user is not self and not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(followers.c.followed_id == user.id).count() > 0

    def post_feed(self):
        """
        Method to retrieve the posts of all users followed by the current user (including himself)
        :return: list of posts
        """
        others = Post.query.join(
            followers, (followers.c.followed_id == Post.user)
        ).filter(
            (followers.c.follower_id == self.id)
        )
        myself = Post.query.filter_by(user=self.id)
        return myself.union(others).order_by(Post.date.desc())

    def get_followers_count(self):
        return self.followers.count()

    def get_followed_count(self):
        return self.followed.count()

    def get_reset_pass_token(self, expire_in=600):
        return jwt.encode(
            {
                'reset_pass': self.id,
                'exp': time() + expire_in,
            },
            current_app.config['SECRET_KEY'],
            algorithm='HS256'
        ).decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_pass']
        except:
            return
        return User.query.get(id)


class SearchableMixin(object):
    @classmethod
    def search(self, query, page, page_size):
        ids, total = query_index(
            self.__tablename__, query, page=page, page_size=page_size)
        if total == 0:
            return Post.query.filter_by(id=0), 0
        ret = []
        print('[INFO] : total is {}'.format(total))
        for i in range(len(ids)):
            ret.append((ids[i], i))
        return self.query.filter(self.id.in_(ids)).order_by(
            db.case(ret, value=self.id)), total

    @classmethod
    def before_commit(self, session):
        session._changes = {
            'add': list(session.new),
            'update': list(session.dirty),
            'delete': list(session.deleted)
        }

    @classmethod
    def after_commit(self, session):
        for obj in session._changes['add']:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes['update']:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes['delete']:
            if isinstance(obj, SearchableMixin):
                remove_from_index(obj.__tablename__, obj)
        session._changes = None

    @classmethod
    def reindex(cls):
        for obj in cls.query:
            add_to_index(cls.__tablename__, obj)


class Post(db.Model, SearchableMixin):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(140))
    date = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    user = db.Column(db.Integer, db.ForeignKey('user.id'))
    language = db.Column(db.String(5))
    __searchable__ = ['content']

    def __repr__(self):
        return 'Post <{}:{}>'.format(self.user, self.date)


db.event.listen(db.session, 'before_commit', SearchableMixin.before_commit)
db.event.listen(db.session, 'after_commit', SearchableMixin.after_commit)
