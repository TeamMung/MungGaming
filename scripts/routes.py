#!/usr/bin/env python3

import flask

gamelist = flask.Blueprint("gamelist", __name__, template_folder="templates")


@gamelist.route("/static/<path:path>",  endpoint="static", methods=["GET"])
def sendStatic(path):
    """Send all files in the static folder"""
    return flask.send_from_directory("static", path)


@gamelist.route("/",  endpoint="index", methods=["GET"])
def index():
    """Send index page"""
    return flask.render_template("index.html")

@gamelist.route("/login", endpoint="login", methods=["GET", "POST"])
def login():
    """Send log-in page"""

    if flask.request.method == 'POST':
        username = flask.request.form['username']
        password = flask.request.form['password']
        
        passwordValid = db.checkPassword(username, password) == False
        return flask.render_template("login.html",
            passwordValid=passwordValid)
    else:
        return flask.render_template("login.html", passwordValid=True)

@gamelist.route("/",  endpoint="register", methods=["POST"])
def register():

    username = flask.request.form['username']
    password = flask.request.form['password']
    email = flask.request.form['email']
    dob = flask.request.form['dob']
    phonenumber = flask.request.form['phonenumber']

    db.addUser(username, password, email, dob, phonenumber)


    """Send register page"""
    return flask.render_template("index.html")


if "__main__" == __name__:
    import database
    db = database.database("../data/")
