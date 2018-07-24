from flask import Flask, render_template, request
from flask import make_response
from flask import render_template, flash, redirect, session, url_for, request, g
from flask import jsonify
#from flask_login import login_user, logout_user, current_user, login_required
from datetime import datetime, timedelta
import json
import urllib2
import requests
from flask import send_file
import datetime
import os

import MySQLdb
import webapp2
import sys
now = datetime.datetime.now()

app = Flask(__name__)
app.config.update(
    PROPAGATE_EXCEPTIONS = True)

# These environment variables are configured in app.yaml.
CLOUDSQL_CONNECTION_NAME = os.environ.get('CLOUDSQL_CONNECTION_NAME')
CLOUDSQL_USER = os.environ.get('CLOUDSQL_USER')
CLOUDSQL_PASSWORD = os.environ.get('CLOUDSQL_PASSWORD')


def connect_to_cloudsql():
    # When deployed to App Engine, the `SERVER_SOFTWARE` environment variable
    # will be set to 'Google App Engine/version'.
    if os.getenv('SERVER_SOFTWARE', '').startswith('Google App Engine/'):
        # Connect using the unix socket located at
        # /cloudsql/cloudsql-connection-name.
        cloudsql_unix_socket = os.path.join(
            '/cloudsql', CLOUDSQL_CONNECTION_NAME)

        db = MySQLdb.connect(
            unix_socket=cloudsql_unix_socket,
            user=CLOUDSQL_USER,
            db="babelli_library_test",
            passwd="",
            charset='ascii')

    # If the unix socket is unavailable, then try to connect using TCP. This
    # will work if you're running a local MySQL server or using the Cloud SQL
    # proxy, for example:
    #
    #   $ cloud_sql_proxy -instances=your-connection-name=tcp:3306
    #
    else:
        db = MySQLdb.connect(
            host='127.0.0.1',
            user=CLOUDSQL_USER,
            passwd="",
            db="babelli_library_test",
            use_unicode=True,
            charset='ascii')

    return db



class Book(object):
    def __init__(self, title, author, bookid, textlink, epublink):
        self.title = title
        self.author = author
        self.bookid = bookid
        self.textlink= textlink
        self.epublink = epublink

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)





def getText(bookid):

    linkTxt = "http://www.copypastapublishing.com/gutenberg"
    formula = list(bookid)
    my_list_len = len(formula)
    for h in range(0, my_list_len - 1):
        linkTxt = linkTxt + "/" + formula[h]
    textLink = linkTxt + "/" + bookid + "/" + bookid + ".txt"
    return textLink

def sfunction(tokens):
    db = connect_to_cloudsql()
    cursor = db.cursor()
    query = ("SELECT * FROM books WHERE title LIKE \'%"+" ".join(tokens)+"%\' OR author LIKE \'%"+" ".join(tokens)+"%\' OR subject LIKE \'%"+" ".join(tokens)+"%\'")
    cursor.execute(query)
    data=cursor.fetchall()
    Ids=[]

    for bookdata in data:
        print(bookdata)
        title=str(bookdata[0])
        author=str(bookdata[1])
        bookid=str(bookdata[2])

        book = Book(title, author, str(bookid), "", "")

        cstext = "http://storage.googleapis.com/babelli-epubs/text/"
        csepub = "http://storage.googleapis.com/babelli-epubs/epub/"
        epub = csepub + "pg" + str(bookid)+ "-images.epub"
        textl = cstext + str(bookid)+ ".txt"
        book.epublink = epub
        book.textlink = textl
        Ids.append(book)
    RESULTS = set(Ids)
    Ids = list(RESULTS)
    print(Ids)
    return Ids
"""
    index = json.load(open('index.json'))
    ids = json.load(open('ids'))
    authors = json.load(open('authors2'))
    IDresults = []

    Ids=[]
    if len(tokens) > 1:
        for i in tokens:
            if IDresults == []:
                try:
                    IDresults.extend(index[i])
                except KeyError:
                    continue
            else:
                try:
                    IDresults = set(IDresults).intersection(index[i])
                except KeyError:
                    continue
    else:
        try:
            IDresults = index[tokens[0]]
        except KeyError:
            IDresults = []
    Ids = []
    for q in IDresults:
        try:
            try:
                title = ids.get(str(q))
            except KeyError:
                title = "none"
                print("error")
            try:
                author = authors.get(str(q))
            except KeyError:
                author = "none"
            bookid = str(q)
            book = Book(title, author, bookid, "", "")
            cstext="http://storage.googleapis.com/babelli-epubs/text/"
            csepub="http://storage.googleapis.com/babelli-epubs/epub/"
            epub = csepub  +"pg" + bookid + "-images.epub"
            textl = cstext+bookid+".txt"
            book.epublink = epub
            book.textlink = textl
            Ids.append(book)
        except ValueError:
            continue
    RESULTS = set(Ids)
    Ids = list(RESULTS)
    print(Ids)
    return Ids
"""""

 # a route for generating sitemapindex.xml
@app.route('/sitemapindex.xml', methods=['GET'])
def sitemapindex():
    """Generate sitemapindex.xml. Makes a list of urls and date modified."""
    sitemap=open("sitemapindex.xml",mode="r")
    website = make_response(sitemap.read())
    website.headers["Content-Type"] = "application/xml"
    assert isinstance(website, object)
    return website


@app.route('/sitemap.1.txt', methods=['GET'])
def sitemap1():
    return app.send_static_file('sitemap.1.txt')

@app.route("/sitemap.2.txt")
def sitemap2():
    return app.send_static_file('sitemap.2.txt')


@app.route('/')
@app.route('/index')
def form():
    results = []
    tokens = ["science", "fiction"]
    results=sfunction(tokens)
    return render_template('main.html', query="science fiction", results=results).encode( "utf-8" )


@app.route('/submitted', methods=['POST'])
def submitted_form():
    query = request.form['search']
    return redirect(url_for('search_results', query=query))


@app.route('/page/<bookid>')
def page(bookid):

    ids = json.load(open("Gutenberg.json"))
    id = ids[bookid]["id"]
    try:
        subject = ids[bookid]["subjects"]
        subject = " ".join(subject).replace(" -- ","\n")
    except TypeError:
        subject = "none"
    try:
        author = ids[bookid]["author"]
    except TypeError:
        author = "none"
    try:
        title = ids[bookid]["title"]
    except TypeError:
        title="none"

    baseLink = "http://www.copypastapublishing.com/gutenberg/"
    linkTxt=getText(bookid)
    epub = baseLink + "cache/epub/" + str(bookid) + "/"
    book = Book(title, author, bookid, linkTxt, epub)
    result=book
    return render_template('page_render.html', subject=subject, result=result)


@app.route('/search_results/<query>', methods=["GET"])
def search_results(query):

    results = []
    tokens = query.lower().split(" ")
    results=sfunction(tokens)
    return render_template('main.html', query=query, results=results)


@app.route('/appsearch/<query>', methods=["GET"])
def appsearch(query):
    tokens = query.lower().split(" ")
    results=sfunction(tokens)
    jsonList=json.dumps([ob.__dict__ for ob in results])
    response = app.response_class(
        response=jsonList,
        status=200,
        mimetype='application/json')
    return response

