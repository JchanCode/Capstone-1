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

    user_following_id = db.Column( db.Integer,
                                   db.ForeignKey("users.id",
                                   ondelete="cascade"),
                                   primary_key=True)

class Likes(db.Model):
    """
    Mapping user likes to warbles
    """

    __tablename__ = "likes"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="cascade"))
    chatter_id = db.Column(db.Integer, db.ForeignKey("chatters.id", ondelete="cascade"), unique=True)


class Comment(db.Model):
    """
    An individual comments on chatter
    """

    __tablename__ ="comments"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="cascade"), nullable=False)
    chatter_id = db.Column(db.Integer, db.ForeignKey("chatters.id", ondelete="cascade"))
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())
    body = db.Column(db.Text, nullable=False)

    user = db.relationship("User")


class User(db.Model):
    """
    User Model in system
    """

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(20), unique=True,nullable=False)
    password = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.Text, default="/static/images/default-pic.png", nullable=True)
    bio = db.Column(db.Text, nullable=True)
    location = db.Column(db.Text, nullable=True)

    chatters = db.relationship("Chatter")

    followers = db.relationship("User",
                                secondary="follows",
                                primaryjoin=(Follows.user_being_followed_id == id),
                                secondaryjoin=(Follows.user_following_id == id))
                                
    following = db.relationship("User",
                                secondary="follows",
                                primaryjoin=(Follows.user_following_id == id),
                                secondaryjoin=(Follows.user_being_followed_id == id))

    likes = db.relationship("Chatter", secondary="likes")

    comments = db.relationship("Chatter", secondary="comments")

    watchlist = db.relationship("Stock",
                                secondary="watchlist")

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

    def liked_chatters_id_list(self):
        """Return User's liked msg id"""

        liked_chatters_id = [chatter.id for chatter in self.likes]
        return liked_chatters_id
    
    def watchlist_list(self):
        """
        Return User's watchlist stock's id
        """

        watchlist_list = [stock.id for stock in self.watchlist]
        return watchlist_list

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
                    location=location)

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


class Chatter(db.Model):
    """
    An individual chatter
    """

    __tablename__ = "chatters"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete='cascade'), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())
    title = db.Column(db.String(140), nullable=False,)
    body = db.Column(db.Text, nullable=False)
    media_link = db.Column(db.Text, nullable=True)

    user = db.relationship("User")
    comments = db.relationship("Comment")


class Stock(db.Model):
    """
    An individual Stock
    """

    __tablename__ = "stocks"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    symbol = db.Column(db.String(10), nullable=False, unique=True)
    assettype = db.Column(db.String)
    exchange = db.Column(db.String)
    industry = db.Column(db.String)
    weekhigh = db.Column(db.Float)
    weeklow = db.Column(db.Float)

    


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
    comment_id = db.Column(db.Integer, db.ForeignKey("comments.id", ondelete="cascade"))


def connect_db(app):
    """
    Connect this database to provided Flask app.
    Im calling this in my Flask app.
    """

    db.app = app
    db.init_app(app)