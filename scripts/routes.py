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

@gamelist.route("/login", endpoint="login", methods=["GET"])
def index():
    """Send log-in page"""
    return flask.render_template("login.html")



if "__main__" == __name__:
    import database
    db = database.database("../data/")
