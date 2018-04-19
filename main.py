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
from flask_sitemap import Sitemap, sitemap_page_needed


app = Flask(__name__)
app.config.update(
    PROPAGATE_EXCEPTIONS = True
)
def getText(bookid):

    linkTxt = "http://www.copypastapublishing.com/gutenberg"
    formula = list(bookid)
    my_list_len = len(formula)
    for h in range(0, my_list_len - 1):
        linkTxt = linkTxt + "/" + formula[h]
    textLink = linkTxt + "/" + bookid + "/" + bookid + ".txt"
    return textLink

def sfunction(tokens):
    gutenberg = json.load(open('index.json'))
    ids = json.load(open('ids'))
    authors = json.load(open('authors2'))
    results = []
    IDresults = []
    previous = []
    epub=''
    if len(tokens) > 1:
        for g in tokens:

            Ids = []
            try:
                Ids = gutenberg[g]
            except KeyError:
                continue
            RESULTS = set(Ids)
            Ids = list(RESULTS)
            if IDresults == []:
                IDresults.extend(Ids)

            try:
                IDresults = set(Ids).intersection(previous)
                if len(IDresults) > 100:
                    break
            except TypeError:
                continue
            previous = Ids
    else:
        try:
            IDresults = gutenberg[tokens[0]]
        except KeyError:
            IDresults = []
    Ids = []
    for q in IDresults:
        try:
            try:
                title = ids.get(str(q))
            except KeyError:
                title = "none"
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

            results.append(book)
        except ValueError:
            continue
    RESULTS = set(results)
    results = list(RESULTS)
    return results

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
    tokens = ["prince"]
    results=sfunction(tokens)
    return render_template('main.html', query="", results=results)

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