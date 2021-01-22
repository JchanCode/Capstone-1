from datetime import datetime
from enum import unique

from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

bcrypt = Bcrypt()
db = SQLAlchemy()



class Follows(db.Model):
    """
    Connection of a follower <-> followed_user
    """

    __tablename__ = "follows"

    user_being_followed_id = db.Column( db.Integer,
                                        db.ForeignKey("users.id",
                                        ondelete="cascade"),
                                        primary_key=True)

    user_following_id = db.Column( db.Column(
                                   db.Integer,
                                   db.ForeignKey("user.id",
                                   ondelete="cascade"),
                                   primary_key=True)
        )

class Likes(db.Model):
    """
    Mapping user likes to warbles
    """

    __tablename__ = "likes"

    id = db.Column(db.Integer, primary_key=True, auto_increment=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="cascade"))
    post_id = db.Column(db.Integer, db.ForeignKey("posts.id", ondelete="cascade"), unique=True)

class User(db.Model):
    """
    User Model in system
    """

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, auto_increment=True)
    username = db.Column(db.String(20), unique=True,nullable=False)
    password = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.Text, default="/static/images/default-pic.png", nullable=True)
    bio = db.Column(db.Text, nullable=True)
    location = db.Column(db.Text, nullable=True)

    messages = db.relationship('Post')

    followers = db.relationship("User",
                                secondary="follows",
                                primaryjoin=(Follows.user_being_followed_id == id),
                                secondaryjoin=(Follows.user_following_id == id))
                                
    following = db.relationship("User",
                                secondary="follows",
                                primaryjoin=(Follows.user_following_id == id),
                                secondaryjoin=(Follows.user_being_followed_id == id))

    def __repr__(self):
        return f"<User #{self.id}: {self.username}>"

    def is_followed_by(self, other_user):
        """Is this user followed by "other_user"""

        found_user_list = [user for user in self.followers if user == other_user]
        return len(found_user_list) == 1

    def is_following(self, other_user):
        """Is this user following "other_user"? """

        found_user_list = [user for user in self.following if user == other_user]
        return len(found_user_list) == 1
    
    @classmethod
    def signup(cls, username, password, image_url, bio, location):
        """
            Signup User User.signup() 
            Hashes password and adds user to system. 
        """

        hashed_pwd = bcrypt.generate_password_hash(password).decode("UTF-8")

        user = User(username=username,
                    password=hashed_pwd,
                    image_url=image_url,
                    bio=bio,
                    location=location,)

        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username,password):
        """
            It searches for a user whose password hash matches this password
            and, if it finds such a user, returns that user object.
        """

        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth=bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False

class Post(db.Model):
    """
    An individual post
    """

    __tablename__ = "posts"

    id = db.Column(db.Integer, primary_key=True, auto_increment=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete='cascade'), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())
    is_portfolio = db.Column(db.Boolean,nullable=False, default=False)
    title = db.Column(db.String(250), nullable=False)
    body = db.Column(db.text, nullable=False)
    media_link = db.Column(db.text, nullable=True)

    user = db.relationship("User")

class Comment(db.Model):
    """
    An individual comments on post
    """

    __tablename__ = "comments"

    id = db.Column(db.Integer, primary_key=True, auto_increment=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="cascade"), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey("posts.id", ondelete="cascade"))
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())
    body = db.Column(db.text, nullable=False)



class Stock(db.Model):
    """
    An individual Stock
    """

    __tablename__ = "stocks"

    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(10), nullable=False, unique=True)
    description = db.Column(db.String(100), nullable=False, unique=True)
    
class Watchlist(db.Model):
    """
    Watchlist connection between User <-> Stock
    """

    __tablename__= "watchlist"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="cascade"))
    stock_id = db.Column(db.Integer, db.ForeignKey("stocks.id"))

class Like_WL(db.Model):
    """
    Watchlist's Like
    """

    __tablename__ = "likes_wl"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="cascade"))
    comment_id = db.Column(db.Integer, db.ForeignKey("comments.id"), ondelete="cascade")


def connect_db(app):
    """
    Connect this database to provided Flask app.
    Im calling this in my Flask app.
    """

    db.app = app
    db.init_app(app)