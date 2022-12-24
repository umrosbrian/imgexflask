from imgexflask import app
import sys, os
from flask import Flask, render_template
from flask_flatpages import FlatPages

#@app.route('/')
#def index():
#    user = {'username': 'Brian'}
#    return render_template('index.html', title='Home', user=user)

# Some configuration, ensures
# 1. Pages are loaded on request.
# DEBUG = True
# FLATPAGES_AUTO_RELOAD = DEBUG
FLATPAGES_EXTENSION = '.php'

# This is somehow setting the path to the 'pages' directory
app.config.from_object(__name__)
pages = FlatPages(app)


# URL Routing - Home Page
@app.route('/')
def index():
    # Articles are pages with a publication date
    articles = (p for p in pages if 'published' in p.meta)
    print([p for p in pages])

    # Show the 10 most recent articles, most recent first.
    latest = sorted(articles, reverse=True,
                    key=lambda p: p.meta['published'])

    print (latest)
    return render_template('index.html', articles=latest[:10])

# URL Routing - Flat Pages
# Retrieves the page path and
@app.route('/<path:path>')
def page(path):
    page = pages.get_or_404(path)
    return render_template("page.html", page=page)
