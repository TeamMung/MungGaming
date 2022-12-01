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
def registerGet():
    """Send register page"""
    return flask.render_template("register.html")


@gamelist.route("/register", endpoint="registerPost", methods=["POST"])
def registerPost():
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


@gamelist.route("/game/add", endpoint="addGameGet", methods=["GET"])
def addGameGet():
    """Send the page for adding a new game"""
    genres = db.getGenres()
    publishers = db.getPublishers()

    return flask.render_template("addGame.html", genres=genres, genreCount=len(genres), publishers=publishers, publisherCount=len(publishers))


# i changed it to localhost/game/add - try again maybe it was because it had uppercase in the url
# also try installing the depenencies - maybe its because its not using waitress


@gamelist.route("/game/add", endpoint="addGamePost", methods=["POST"])
def addGamePost():
    """Processes the new game form and adds game to the database"""
    genres = db.getGenres()
    publishers = db.getPublishers()

    gameTitle = flask.request.form["gameName"]
    desc = flask.request.form["desc"]
    releaseDate = flask.request.form["releaseDate"]
    gameGenres = flask.request.form["genres"]
    publisher = flask.request.form["publishers"]

    for value, validate in [
        (gameTitle, db.validator.gameTitle),
        (releaseDate, db.validator.releaseDate)
    ]:
        valid, message = validate(value)
        if not valid:
            return flask.render_template("addGame.html", error=message, 
                genres=genres, genreCount=len(genres),
                publishers=publishers, publisherCount=len(publishers),
                gameName=gameTitle,  desc=desc, releaseDate=releaseDate)

    db.addGame(gameTitle, desc, releaseDate, gameGenres, publisher)

    return flask.redirect(flask.url_for("gamelist.allGames"))


##@gamelist.route("/game/add", endpoint="addGamePost", methods=["POST"])
##def allGames():
    """Add the game to the database"""
    ## todo: validate the data
    ## idk probably some more stuff
    ## dont need to validate the genres and publishers because they are from a dropdown and if a user manages to fuck that up somehow the database will just ignore it
    ## theres no requirements for description so im not bothering with that
    ## upload the image seperately like the pfp
    ## game is currently always unapproved but i can add that later
    return flask.render_template("addGame.html")


if "__main__" == __name__:
    import database
    import validator
    db = database.database("../data/", validator.validator)
