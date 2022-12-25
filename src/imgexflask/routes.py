import logging
from imgexflask import app
from flask import render_template, request, session
from flask_flatpages import FlatPages
from werkzeug.security import check_password_hash
import datetime as dt
import os


current_time = dt.datetime.now().strftime('%Y%m%d_%H%M%S')
log_file_aps = os.path.join(os.path.dirname(os.path.dirname(app.instance_path)), 'logs', f"{current_time}.log")
logging.basicConfig(filename=log_file_aps,
                    filemode='w',
                    level=logging.DEBUG,
                    format='%(levelname)s-%(asctime)s-%(funcName)s - %(message)s')

# Files having this extension will be the only ones that are returned from the 'pages' directory.
FLATPAGES_EXTENSION = '.php'
# This is relative to the app root, which is within the package directory.
FLATPAGES_ROOT = os.path.join(os.pardir, os.pardir, os.pardir, 'pages')

# This is somehow setting the path to the 'pages' directory.  Don't see anything in app.config that's changed.
app.config.from_object(__name__)
pages = FlatPages(app)

# I think this is needed for request...it's not just a WTF thing
app.config["SECRET_KEY"] = 'e^Px\9]D@g*"*`^:+4+T'


@app.route('/')
@app.route('/index')
def home():
    # Don't know why I can't use session['logged_in'].
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        # Articles are pages with a publication date
        articles = (p for p in pages if 'published' in p.meta)
        print(f"p in pages: {[p for p in pages]}")
        print(f"p.meta in pages: {[p.meta for p in pages]}")

        # Show the 10 most recent articles, most recent first.
        latest = sorted(articles, reverse=True,
                        key=lambda p: p.meta['published'])

        print (latest)
        return render_template('index.html', articles=latest[:10])


# I found that if I put in the URL for index after logging out the template would be rendered.  This prevents that \
# behavior
@app.route('/login')
def login_get():
    if session['logged_in']:
        return render_template('index.html')
    else:
        return render_template('login.html')


# werkzeug is installed as a dependency of flask.  You can use `from werkzeug.security import generate_password_hash` \
# then print(generate_password_hash(<password>, 'sha256')) to generate the hash of <password>.  You can then hardcode \
# this hashed password and test to see if the provided password's hash matches the hardcoded hash.
# https://pythonspot.com/login-authentication-with-flask/ for this method of the form & session method of authentication
@app.route('/login', methods=['POST'])
def do_admin_login():
    provided_uname = request.form['username']
    provided_pword = request.form['password']
    hashed_pword = 'sha256$qy5yj2dnBfKzDSzy$97b4acbbd4d593bb299efbc73e2c5a1c0a8382693a243b868f2466ca817067e3'
    # The hash of the provided password when correct will be different every time so we can't use a simple string \
    # comparison.  We need to use check_password_hash().
    if provided_uname == 'admin' and check_password_hash(hashed_pword, provided_pword):
        session['logged_in'] = True
        logging.debug(f"{provided_uname} logged in")
    else:
        logging.warning(f"User {provided_uname} attempted to log in with password {provided_pword}.")
    return render_template('index.html')


@app.route("/logout")
def logout():
    session['logged_in'] = False
    logging.debug(f"logged out")
    return render_template('login.html')


# URL Routing - Flat Pages
# Retrieves the page path and
@app.route('/<path:path>')
def page(path):
    if session['logged_in']:
        page = pages.get_or_404(path)
        return render_template("page.html", page=page)
    else:
        return render_template('login.html')
