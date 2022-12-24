from imgexflask import app
from flask import render_template, request, session
from flask_flatpages import FlatPages


# Some configuration, ensures
# 1. Pages are loaded on request.
# DEBUG = True
# FLATPAGES_AUTO_RELOAD = DEBUG
FLATPAGES_EXTENSION = '.php'

# This is somehow setting the path to the 'pages' directory.  Don't see anything in app.config that's changed.
app.config.from_object(__name__)
pages = FlatPages(app)

# I think this is needed for request...it's not just a WTF thing
app.config["SECRET_KEY"] = "ITSASECRET"


# URL Routing - Flat Pages
# Retrieves the page path and
@app.route('/<path:path>')
def page(path):
    if session['logged_in']:
        page = pages.get_or_404(path)
        return render_template("page.html", page=page)
    else:
        return home()


@app.route('/')
def home():
    if not session['logged_in']:
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

@app.route('/login', methods=['POST'])
def do_admin_login():
    if request.form['username'] == 'admin' and request.form['password'] == 'p':
        session['logged_in'] = True
    return home()

@app.route("/logout")
def logout():
    session['logged_in'] = False
    return home()