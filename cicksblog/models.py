from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from cicksblog import db, login_manager
from flask import current_app
from flask_login import UserMixin
from datetime import datetime


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    phone_number = db.Column(db.String(32), nullable=False)
    password = db.Column(db.String(60), nullable=False)
    user_pict = db.Column(db.String(255), default="default.jpg", nullable=False)
    posts = db.relationship("Post", backref="author", lazy=True)

    @staticmethod
    def token_verification(token):
        s = Serializer(current_app.config["SECRET_KEY"])

        try:
            user_id = s.loads(token)["user_id"]
        except:
            return None

        return User.query.get(user_id)

    def get_token(self, expire_in=1800):
        s = Serializer(current_app.config["SECRET_KEY"], expire_in)
        return s.dumps({"user_id": self.id}).decode("utf-8")

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.user_pict}')"


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, default=datetime.utcnow(), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"