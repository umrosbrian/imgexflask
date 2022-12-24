from imgexflask import app
import sys, os
from flask import Flask, render_template, Response
from flask_flatpages import FlatPages
from flask_login import LoginManager, UserMixin, login_required


# Some configuration, ensures
# 1. Pages are loaded on request.
# DEBUG = True
# FLATPAGES_AUTO_RELOAD = DEBUG
FLATPAGES_EXTENSION = '.php'

# This is somehow setting the path to the 'pages' directory
app.config.from_object(__name__)
pages = FlatPages(app)

# Instantiate LoginManager
login_manager = LoginManager()
login_manager.init_app(app)
app.config["SECRET_KEY"] = "ITSASECRET"


## URL Routing - Home Page
#@app.route('/')
#def index():
#    # Articles are pages with a publication date
#    articles = (p for p in pages if 'published' in p.meta)
#    print([p for p in pages])
#
#    # Show the 10 most recent articles, most recent first.
#    latest = sorted(articles, reverse=True,
#                    key=lambda p: p.meta['published'])
#
#    print (latest)
#    return render_template('index.html', articles=latest[:10])


# URL Routing - Flat Pages
# Retrieves the page path and
@app.route('/<path:path>')
def page(path):
    page = pages.get_or_404(path)
    return render_template("page.html", page=page)


# http://gouthamanbalaraman.com/blog/minimal-flask-login-example.html for authentication without db
class User(UserMixin):
    # proxy for a database of users
    user_database = {"JohnDoe": ("JohnDoe", "John"),
               "JaneDoe": ("JaneDoe", "Jane")}

    def __init__(self, username, password):
        self.id = username
        self.password = password

    @classmethod
    def get(cls,id):
        return cls.user_database.get(id)

# Return a User instance if credentials are valid, otherwise return None
@login_manager.request_loader
def load_user(request):
    token = request.headers.get('Authorization')
    if token is None:
        token = request.args.get('token')

    if token is not None:
        username,password = token.split(":") # naive token
        user_entry = User.get(username)
        if (user_entry is not None):
            user = User(user_entry[0],user_entry[1])
            if (user.password == password):
                return user
    return None

@app.route("/",methods=["GET"])
def index():
    return Response(response="Hello World!",status=200)

# The token needs to be provided in the URL.  E.g. http://localhost:5000/protected/?token=JohnDoe:John
@app.route("/protected/",methods=["GET"])
@login_required
def protected():
    return Response(response="Hello Protected World!", status=200)