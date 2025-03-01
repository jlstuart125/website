from flask import Flask
from flask import render_template
from flask import url_for

app = Flask(__name__)

@app.route("/")
def index():
    return render_template(
        "main.html", 
        imgpath=url_for('static', filename='image/favicon.png'),
        stylepath=url_for('static', filename='style.css') 
    )

@app.route("/hello/")
@app.route("/hello/<name>")
def hello(name=None):
    return render_template("hello.html", person=name)

@app.route("/about")
def about():
    return render_template("main.html")