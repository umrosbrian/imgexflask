import logging
from imgexflask import app
from flask import render_template, request, session, send_from_directory
from flask_flatpages import FlatPages
from werkzeug.security import check_password_hash
import datetime as dt
import os


current_time = dt.datetime.now().strftime('%Y%m%d_%H%M%S')
log_file_aps = os.path.join(os.path.dirname(os.path.dirname(app.root_path)), 'logs', f"{current_time}.log")
logging.basicConfig(filename=log_file_aps,
                    filemode='w',
                    level=logging.DEBUG,
                    format='%(levelname)s-%(asctime)s-%(funcName)s - %(message)s')


# Files having this extension will be the only ones that are returned from the 'pages' directory.
FLATPAGES_EXTENSION = '.html'
# Directory containing the files that will be rendered with page().
FLATPAGES_ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(app.root_path))), 'pages')
logging.debug(f"FLATPAGES_ROOT: {FLATPAGES_ROOT}")
logging.debug(f"os.listdir(FLATPAGES_ROOT): {os.listdir(FLATPAGES_ROOT)}")


# This is somehow setting the path to the 'pages' directory.  Don't see anything in app.config that's changed.
app.config.from_object(__name__)
pages = FlatPages(app)

# I think this is needed for request...it's not just a WTF thing
app.config["SECRET_KEY"] = 'e^Px\9]D@g*"*`^:+4+T'

app.config['DOWNLOAD_DIR'] = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(app.root_path))), 'download')
logging.debug(f"app.config['DOWNLOAD_DIR']: {app.config['DOWNLOAD_DIR']}")


@app.route('/')
@app.route('/index')
def home():
    # The session object may not have the key 'logged_in' yet so we use .get to avoid a KeyError if it doesn't.
    if not session.get('logged_in'):
        logging.debug(f"The 'logged_in' key wasn't present when home() was issued.  Setting it to True and rendering"
                      f"index.html")
        session['logged_in'] = True  # added for troubleshooting
        return render_template('index.html')  # added for troubleshooting
         # return render_template('login.html')
    else:
        logging.debug(f"The 'logged_in' key was found when home() was issued.  It current value is "
                      f"{session['logged_in']}.  Setting it to True and rendering index.html")
        session['logged_in'] = True  # added for troubleshooting
        return render_template('index.html')


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
    provided_username = request.form['username']
    provided_password = request.form['password']
    hashed_password = 'sha256$qy5yj2dnBfKzDSzy$97b4acbbd4d593bb299efbc73e2c5a1c0a8382693a243b868f2466ca817067e3'
    # The hash of the provided password when correct will be different every time, so we can't use a simple string \
    # comparison.  We need to use check_password_hash().
    if provided_username == 'admin' and check_password_hash(hashed_password, provided_password):
        session['logged_in'] = True
        logging.debug(f"User '{provided_username}' logged in.")
        return render_template('index.html')
    else:
        logging.warning(f"User '{provided_username}' attempted to log in with password '{provided_password}'.")
        return render_template('login.html')


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
        logging.debug(f"page({path}) called.  Rendering {page} via page.html.")
        #return render_template('index.html')
        return render_template("page.html", page=page)
    else:
        return render_template('login.html')


# Download file in 'download' directory.
@app.route('/download/<path:filename>')
def download(filename):
    # path_to_ = os.path.join(app.root_path, app.config['DOWNLOAD_DIR'])
    logging.debug("Downloading setup.cfg")
    return send_from_directory(directory=app.config['DOWNLOAD_DIR'], path=filename)


@app.route('/private_template')
def private_template():
    logging.debug("rendering private_template.html")
    return render_template('private_template.html')


@app.route('/index_copy')
def index_copy():
    logging.debug("rendering index_copy.html")
    return render_template('index_copy.html')
