"""Time use"""
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db, login
from hashlib import md5


class User(UserMixin, db.Model):
    """User Table"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(120))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    about_me = db.Column(db.String(140))

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def create_password(self, password):
        """Create Password Hash"""
        self.password_hash = generate_password_hash(password)

    def identify_password(self, password):
        """Identify Password"""
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        return "https://www.gravatar.com/avatar/{}?d=identicon&s={}".format(md5(self.email.lower().encode('utf-8')).hexdigest(), size)


class Post(UserMixin, db.Model):
    """Post Table"""
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post {}>'.format(self.body)


@login.user_loader
def load_user(userid):
    return User.query.get(userid)
