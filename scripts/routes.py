#!/usr/bin/env python3

import flask

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


if "__main__" == __name__:
    import database
    import validator
    db = database.database("../data/", validator.validator)
