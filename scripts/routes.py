#!/usr/bin/env python3

import flask

gamelist = flask.Blueprint("gamelist", __name__, template_folder="templates")


@gamelist.route("/static/<path:path>", methods=["GET"])
def sendStatic(path):
    """Send all files in the static folder"""
    return flask.send_from_directory("static", path)


@gamelist.route("/", methods=["GET"])
def index():
    """Send index page"""
    return flask.render_template("index.html")
