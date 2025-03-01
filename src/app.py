from flask import Flask
from flask import render_template
from flask import url_for

app = Flask(__name__)

class Page:
    def __init__(self, href, caption):
        self.href = href
        self.caption = caption

nav_items = []
nav_items.append(Page("hello","Hello"))
nav_items.append(Page("about","About Me"))
nav_items.append(Page("template","Template"))


@app.route("/")
def index():
    return render_template(
        "main.html", 
        imgpath=url_for('static', filename='image/favicon.png')
    )

@app.route("/hello/")
@app.route("/hello/<name>")
def hello(name=None):
    return render_template("hello.html", person=name)

@app.route("/template")
def template(nav=nav_items):
    return render_template("child.html", navigation=nav)

@app.route("/about")
def about():
    return render_template("main.html")