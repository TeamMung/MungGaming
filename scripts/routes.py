#!/usr/bin/env python3

import flask
import hashlib
import os
from PIL import Image

gamelist = flask.Blueprint("gamelist", __name__, template_folder="templates")


@gamelist.route("/static/<path:path>", endpoint="static", methods=["GET"])
def sendStatic(path):
    """Send all files in the static folder"""
    return flask.send_from_directory("static", path)


@gamelist.route("/", endpoint="home", methods=["GET"])
def home():
    """Send home page"""
    return flask.render_template("home.html")


@gamelist.route("/login", endpoint="loginGet", methods=["GET"])
def loginGet():
    """Send login page"""
    return flask.render_template("login.html")


@gamelist.route("/login", endpoint="loginPost", methods=["POST"])
def loginPost():
    """User tries to login"""
    username = flask.request.form['username']
    password = flask.request.form['password']
    
    passwordValid = db.checkPassword(username, password)
    if (passwordValid == False):
        return flask.render_template("login.html",
        passwordValid=passwordValid)
    
    flask.session['username'] = username
    return flask.redirect(flask.url_for("gamelist.allGames"))


@gamelist.route("/register", endpoint="registerGet", methods=["GET"])
def register():
    """Send register page"""
    return flask.render_template("register.html")


@gamelist.route("/register", endpoint="registerPost", methods=["POST"])
def register():
    """User tries to register"""
    username = flask.request.form["username"]
    password = flask.request.form["password"]
    email = flask.request.form["email"]
    dob = flask.request.form["dob"]
    phonenumber = flask.request.form["phonenumber"]
    for value, validate in [
        (username, db.validator.username),
        (password, db.validator.password),
        (email, db.validator.email),
        (dob, db.validator.dateOfBirth),
        (phonenumber, db.validator.phoneNumber)
    ]:
        valid, message = validate(value)
        if not valid:
            return flask.render_template("register.html", error=message,
                username=username, password=password, email=email, dob=dob, phonenumber=phonenumber)

    db.addUser(username, password, email, dob, phonenumber)

    return flask.redirect(flask.url_for("gamelist.loginGet"))


@gamelist.route("/logout", endpoint="logout", methods=["GET"])
def logout():
    """Log out user and send logout page"""
    return flask.render_template("logout.html")


@gamelist.route("/profile", endpoint="profile", methods=["GET"])
def profile():
    """Send profile page"""
    if "username" not in flask.session:
        return flask.redirect(flask.url_for("gamelist.loginGet"))
    return flask.render_template("profile.html")


@gamelist.route("/user", endpoint="user", methods=["GET"])
def profile():
    """Send user page"""
    return flask.render_template("user.html")


@gamelist.route("/games", endpoint="allGames", methods=["GET"])
def allGames():
    """Send all games page"""
    return flask.render_template("allGames.html")


@gamelist.route("/game/<game>", endpoint="game", methods=["GET"])
def game(game):
    """Send a specific game page"""
    return flask.render_template("game.html")


@gamelist.route("/lists", endpoint="lists", methods=["GET"])
def allGames():
    """Send the lists page"""
    return flask.render_template("lists.html")


@gamelist.route("/images/profile/<username>.png", endpoint="pfpGet", methods=["GET"])
def userProfilePicture(username):
    """Get the profile picture of a user"""
    usernameHash = hashlib.md5(username.lower().encode()).hexdigest()
    file = f"{db.directory}/images/pfp/{usernameHash}.png"
    if os.path.exists(file):
        return flask.send_file(file)
    return flask.redirect("/static/images/defaultPFP.png")


@gamelist.route("/images/profile/upload", endpoint="pfpPost", methods=["POST"])
def userProfilePicture():
    """Upload the profile picture of a user"""
    if "username" not in flask.session:
        return {"success": False, "error": "You are not logged in."}, 401
    username = flask.session["username"]
    usernameHash = hashlib.md5(username.lower().encode()).hexdigest()
    file = f"{db.directory}/images/pfp/{usernameHash}.png"
    if "image" not in flask.request.files:
        return {"success": False, "error": "No file was sent."}, 400
    image = Image.open(flask.request.files["image"])
    if image.width < 64 or image.height < 64:
        return {"success": False, "error": "Image is too small."}, 400
    image = image.resize((512, 512), Image.ANTIALIAS)
    image.save(file, "PNG")
    return {"success": True}


if "__main__" == __name__:
    import database
    import validator
    db = database.database("../data/", validator.validator)
