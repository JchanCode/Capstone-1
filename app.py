
from pdb import Pdb
import pdb
from flask import Flask, render_template, request, flash, redirect, session, g, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from secrets import finnhub_apikey, alpha_apikey,news_apikey
import requests, finnhub
from datetime import date, timedelta, datetime
import time
from forms import RegisterUserForm, LoginForm, PostForm, CommentForm
from models import db, connect_db, Follows, Likes, User, Chatter, Comment, Stock, Watchlist
import os

CURR_USER_KEY = "curr_user"

app = Flask(__name__)





app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get('DATABASE_URL',"postgresql:///capstone1")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = True
app.config["SECRET_KEY"] = os.environ.get('SECRET_KEY', 'abc123') 
toolbar = DebugToolbarExtension(app)

finnhub_client = finnhub.Client(api_key="c03or7f48v6sogn2ue9g") 

connect_db(app)


db.drop_all()
db.create_all()

###############################################################################
#
#                         User signup / login / logout
#
#
############################################################################### 

@app.before_request
def add_user_to_g():
    """
    If we're logged in, add curr user to Flask global g.
    """

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None


def do_login(user):
    """
    Log in user.
    """

    session[CURR_USER_KEY] = user.id


def do_logout():
    """
    Logout user.
    """

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]


@app.route("/signup", methods=["POST"])
def signup():
    """
    Handle user signup.

    Create new user and add to DB. Redirect to Homepage.

    If form not valid, present form.

    If Username already exist, flash message and re-present form. 
    """

    signup_form = RegisterUserForm()

    if signup_form.validate_on_submit():
        try:
            user = User.signup( username = signup_form.username.data.lower(),
                                password = signup_form.password.data,
                                image_url = signup_form.image_url.data or User.image_url.default.arg,
                                location = signup_form.location.data,
                                bio = signup_form.bio.data
            )
            db.session.commit()

        except IntegrityError:
            flash("Username already taken", "danger")
            return render_template("/",signup_form=signup_form,)

        do_login(user)

        return redirect("/")

    
    login_form = LoginForm()

    return render_template("homepage.html", signup_form=signup_form, login_form=login_form)


@app.route("/login", methods=["POST"])
def login():
    """
    Handle user login.
    """

    login_form = LoginForm()


    if login_form.validate_on_submit():
        user = User.authenticate(login_form.username.data.lower(),
                                 login_form.password.data)

        if user:
            do_login(user)
            flash(f"Hello, {user.username}!", "success")
            return redirect("/")
  
    else:
    
        flash("Invalid credentails.", "danger")
        signup_form=RegisterUserForm()
        return render_template("homepageNon.html", login_form=login_form, signup_form=signup_form)


@app.route("/logout")
def logout():
    """
    Handle logout of user.
    """

    do_logout()
    flash("Logged Out!", "success")
    return redirect("/")


###############################################################################
#
#                               Stock Routes:
#
#
############################################################################### 


@app.route("/stocks/<string:symbol>")
def stock_profile(symbol):
    """
    Show stock profile
    """

    if not g.user:
        flash("Please log in first!","danger")
        return redirect("/")
    
    overview = get_company_overview(symbol)
    logo_url = get_logo_url(symbol)
    stock = Stock.query.filter_by(symbol=symbol).first()


    post_form = PostForm()

    return render_template("/stocks/s_profile.html",logo_url=logo_url,overview=overview, post_form=post_form, stock=stock)


@app.route("/stocks/<string:symbol>/add",methods=["POST"])
def stock_add(symbol):
    """
    Add Stock to Stocks table
    """

    if not g.user:
        flash("You need to be logged in for this!","danger")
        return redirect("/")

    overview = get_company_overview(symbol)

    user = User.query.get(g.user.id)
    stock = Stock.query.filter_by(symbol=symbol).first()
    if stock is None:

        new_stock = Stock(symbol=overview["Symbol"],
                          name=overview["Name"],
                          assettype=overview["AssetType"],
                          exchange=overview["Exchange"],
                          industry=overview["Industry"],
                          weekhigh=overview["52WeekHigh"],
                          weeklow=overview["52WeekLow"]
                          )
        db.session.add(new_stock)
        db.session.commit()
        user.watchlist.append(new_stock)
        db.session.commit()
    else:
        user.watchlist.append(stock)
        db.session.commit()


    return redirect(f"/stocks/{symbol}")


@app.route("/stocks/<string:symbol>/delete", methods=["POST"])
def stock_delete(symbol):
    """
    Delete Stock From watchlist<------ need to change database?
    """
    if not g.user:
        flash("You need to be logged in for this","danger")
        return redirect("/")

    stock = Stock.query.filter_by(symbol=symbol).first()
    stock_to_delete = Watchlist.query.filter(Watchlist.user_id==g.user.id, Watchlist.stock_id==stock.id).one()
    db.session.delete(stock_to_delete)
    db.session.commit()

    return redirect(f"/stocks/{symbol}")


###############################################################################
#
#                               Search Routes:
#
#
############################################################################### 


@app.route('/search')
def search():
    """
    Search bar route
    """

    search = request.args.get('search')
    symbols = search_symbol(search)
    post_form = PostForm()
    signup_form = RegisterUserForm()
    login_form=LoginForm()

    return render_template('users/index.html',login_form=login_form, post_form=post_form, symbols=symbols, signup_form=signup_form)


###############################################################################
#
#                               User routes:
#
#
############################################################################### 


@app.route("/users/<int:user_id>")
def user_profile(user_id):
    """
    Show user profile
    """

    if not g.user:
        flash("You need to be signed in for this","danger")
        return redirect("/")

    user = User.query.get_or_404(user_id)
    edit_form = RegisterUserForm(obj=user)
    post_form = PostForm()
    following_list = [user.id for user in user.following]

    return render_template("profile.html", user=user,edit_form=edit_form,post_form=post_form,following_list=following_list)



@app.route("/users/delete", methods=["POST"])
def delete_user():
    """
    Delete user.
    """

    if not g.user:
        flash("Access unauthoriezed.","danger")
        return redirect("/")

    do_logout()

    db.session.delete(g.user)
    db.session.commit()

    return redirect("/signup")


@app.route("/users/edit", methods=["POST"])
def edit_user():
    """
    Handle Edit user
    """

    if not g.user:
        flash("Access unauthoriezed.","danger")
        return redirect("/")

    user = User.query.get_or_404(g.user.id)
    signup_form = RegisterUserForm(obj=user)

    if signup_form.validate_on_submit():
        if User.authenticate(signup_form.username.data.lower(), signup_form.password.data):
            user = User.query.get(g.user.id)

            user.username = signup_form.username.data.lower()
            user.password = signup_form.password.data
            user.image_url = signup_form.image_url.data
            user.bio = signup_form.bio.data
            user.location = signup_form.location.data

            db.session.add(user)
            db.session.commit()

            flash("User's info updated","success")
            return redirect(f"/users/{g.user.id}")
        else:
            flash("wrong password","danger")
            return redirect(f"/users/{g.user.id}")

    return render_template(f"/users/{g.user.id}",signup_form=signup_form)

###############################################################################
#
#                               Follow Routes:
#
#
################################################################################


@app.route("/follow/<int:follow_id>", methods=["POST"])
def user_add_follow(follow_id):
    """
    Add a follow for the currently logged in user
    """

    if not g.user:
        flash("You need to be signed in for this","danger")
        return redirect("/")

    followed_user = User.query.get_or_404(follow_id)
    g.user.following.append(followed_user)
    db.session.commit()

    return redirect(f"/chatters")


@app.route("/stop-following/<int:follow_id>", methods=["POST"])
def user_stop_following(follow_id):
    """
    Have currently logged in user stop following this user
    """

    if not g.user:
        flash("You need to be signed in for this","danger")
        return redirect("/")

    followed_user = User.query.get(follow_id)
    g.user.following.remove(followed_user)
    db.session.commit()

    return redirect(f"/chatters")


###############################################################################
#
#                               Chatter Routes:
#
#
#############################################################################


@app.route("/chatters", methods=["GET"])
def chatters_all():
    """
    List all chatter
    """

    if not g.user:
        flash("You need to be logged in to do this", "danger")
        return redirect("/")

    chatters = Chatter.query.all()

    post_form = PostForm()
    liked_chatters_list=g.user.liked_chatters_id_list()
    following_list = [user.id for user in g.user.following]
    return render_template("chatters/all.html", post_form=post_form, chatters=chatters,
    liked_chatters_list=liked_chatters_list, following_list=following_list)


@app.route("/chatters/<int:chatter_id>", methods=["GET"])
def chatter_show(chatter_id):
    """
    Show a chatter
    """

    if not g.user:
        flash("You need to be logged in to do this")
        return redirect("/")

    chatter = Chatter.query.get(chatter_id)
    post_form=PostForm()
    comment_form=CommentForm()
    following_list = [user.id for user in g.user.following]
    return render_template("chatters/chatter.html", chatter=chatter,post_form=post_form, comment_form=comment_form,following_list=following_list)


@app.route("/chatters/add", methods=["POST"])
def chatter_add():
    """
    Add chatter to db
    """

    if not g.user:
        flash("You need to be logged in to do this","danger")
        return redirect("/")

    form = PostForm()
    if form.validate_on_submit():
        new_chatter = Chatter(title=form.title.data,
                              body=form.body.data,
                              media_link=form.media_link.data)
        g.user.chatters.append(new_chatter) 
        db.session.commit()

        return redirect(f"/chatters")


###############################################################################
#
#                               Comment routes:
#
############################################################################### 


@app.route("/comments/<int:chatter_id>/add", methods=["POST"])
def comment_add(chatter_id):
    """
    Add comment to post
    """

    if not g.user:
        flash("You need to be logged in to do this","danger")
        return redirect("/")

    form = CommentForm()
    if form.validate_on_submit():
        new_comment = Comment(body=form.body.data,
                              user_id=g.user.id)
        chatter=Chatter.query.get(chatter_id)
        chatter.comments.append(new_comment)
        db.session.commit()

        return redirect(f"/chatters/{chatter_id}")


###############################################################################
#
#                               Likes routes:
#
#
############################################################################### 


@app.route("/likes/<int:chatter_id>/add", methods=["POST"])
def like_add(chatter_id):
    """
    Adding like to post/user
    """

    if not g.user:
        flash("Please sign in first", "danger")
        return redirect("/")

    user = User.query.get(g.user.id)
    liked_chatter = Chatter.query.get(chatter_id)
    user.likes.append(liked_chatter)
    db.session.commit()

    return redirect("/chatters")


@app.route("/likes/<int:chatter_id>/delete", methods=["POST"])
def like_delete(chatter_id):
    """
    Remove like from a post/user
    """

    if not g.user:
        flash("Please sign in first","danger")
        return redirect("/")

    liked_chatter = Likes.query.filter(Likes.post_id==chatter_id, Likes.user_id==g.user.id).one()
    db.session.delete(liked_chatter)
    db.session.commit()

    return redirect("/chatters")


###############################################################################
#
#                               Homepge and error pages:
#
#
############################################################################### 


@app.route("/")
def homepage():
    """
    Show homepage, fetch news from user watchlist
    """

    signup_form=RegisterUserForm()
    login_form=LoginForm()
    post_form=PostForm()

    if g.user:
        news = get_news(g.user)


        return render_template("homepage.html", signup_form=signup_form,    login_form=login_form, post_form=post_form, news=news, do_format = format_datetime)
    

    
    return render_template("homepageNon.html", signup_form=signup_form, login_form=login_form, post_form=post_form, do_format=format_datetime)
    # general_news = get_general_news()
    # , news=general_news
@app.after_request
def add_header(req):
    """Add non-caching headers on every request."""

    req.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    req.headers["Pragma"] = "no-cache"
    req.headers["Expires"] = "0"
    req.headers['Cache-Control'] = 'public, max-age=0'
    return req


###############################################################################
#
#                                Api Routes:
#
#
############################################################################### 


@app.route("/api/watchlist", methods=["GET"])
def api_watchlist():
    """
    Return watchlist data serialize and jsonify
    """
    user = User.query.get(g.user.id)
    watchlist = [ serialize_watchlist(stock) for stock in user.watchlist]
    
    return jsonify(watchlist)


@app.route("/api/following", methods=["GET"])
def api_following():
    """
    Return watchlist data
    """
    user = User.query.get(g.user.id)
    following = [ serialize_following(user) for user in user.following]

    return jsonify(following)


@app.route("/api/like", methods=["GET"])
def api_like():
    """
    Return like data
    """
    user = User.query.get(g.user.id)
    chatters = [ serialize_like(chatter) for chatter in user.likes ]

    return jsonify(chatters)


@app.route("/api/chatter", methods=["GET"])
def api_chatter():
    """
    Return chatter data
    """
    user = User.query.get(g.user.id)
    chatters = [ serialize_chatter(chatter) for chatter in user.chatters ]
    return jsonify(chatters)


@app.route("/api/follower", methods=["GET"])
def api_follower():
    """
    Return follower data
    """
    user=User.query.get(g.user.id)
    followers = [ serialize_follower(follower) for follower in user.followers ]
    return jsonify(followers)

###############################################################################
#
#                               Helper Functions:
#
#
############################################################################### 
def serialize_follower(follower):
    """
    Serialize a follower Sqlachemy obj into dictionary
    """

    return {
        "id"       : follower.id,
        "username" : follower.username,
        "image_url": follower.image_url,
        "location" : follower.location,
    }



def serialize_chatter(chatter):
    """
    Serialize a chatter Sqlachemy obj into dictionary
    """

    return {
        "id":       chatter.id,
        "user_id":  chatter.user_id,
        "timestamp": chatter.timestamp.strftime('%d %B %Y'),
        "title":    chatter.title,
        "body":     chatter.body,
        "media_link":chatter.media_link,
        "c_length": len(chatter.comments)
    }


def serialize_like(chatter):
    """
    Serialize a like SQLAchemy obj into dictonary
    """

  
    return {
        "id":       chatter.id,
        "user_id":  chatter.user_id,
        "timestamp": chatter.timestamp.strftime('%d %B %Y'),
        "title":    chatter.title,
        "body":     chatter.body,
        "media_link":chatter.media_link,
        "c_length": len(chatter.comments)
    }


def serialize_following(user):
    """
    Serialize a following SQLAchemy obj into dictionary
    """

    return {
        "id"       : user.id,
        "username" : user.username,
        "image_url": user.image_url,
        "location" : user.location,
    }


def serialize_watchlist(watchlist):
    """
    Serialize a watchlist SQLAchemy obj to dictionary
    """

    return {  
            "id"     : watchlist.id,
            "name" : watchlist.name,
            "symbol": watchlist.symbol,
            "assettype":watchlist.assettype,
            "exchange":watchlist.exchange,
            "industry":watchlist.industry,
            "weekhigh":watchlist.weekhigh,
            "weeklow":watchlist.weeklow,
    }


def get_general_news():
    """
    grab general news from api
    """
    general_news = (finnhub_client.general_news("general", min_id=10))

    return general_news 


def get_news(user):
    """
    Get news from user's watchlist        
    """

    today = date.today()
    yesterday = today - timedelta(days = 1)
    user = g.user.watchlist # User[0].symbol
    news = []

    for stock in user:
        news_resp = (finnhub_client.company_news(stock.symbol, _from=yesterday, to=today))
        for new in news_resp:   
            news.append(new)
            
    news.sort(reverse=True, key=get_time)

    return news


def format_datetime(time):
    """
    Takes UNIX timestamp convert into Y M D
    """
    timestamp = datetime.fromtimestamp(time)

    return timestamp


def get_time(new):
    """
    grab new["datetime"] from news
    """ 

    return new["datetime"]


def search_symbol(search):
    """
    Takes search term and fetch api for matching symbol
    """

    response = requests.get(f'https://www.alphavantage.co/query?function=SYMBOL_SEARCH&keywords={search}&apikey={alpha_apikey}')
    res = response.json()
    data = res['bestMatches']

    return data


def get_company_overview(symbol):
    """
    Calls alpha api and fetch comapany's profile using symbol provided 
    """
    
    response = requests.get(f"https://www.alphavantage.co/query?function=OVERVIEW&symbol={symbol}&apikey={alpha_apikey}")
    overview = response.json()

    return overview


def get_logo_url(symbol):
    """
    Calls finnhub's api for company profile
    Extracts company's website 
    """

    for_url = finnhub_client.company_profile2(symbol=symbol)
    logo_url = for_url["weburl"]

    return logo_url
