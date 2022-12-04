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
def user():
    """Send user page"""
    return flask.render_template("user.html")


@gamelist.route("/games", endpoint="allGames", methods=["GET"])
def allGames():
    """Send all games page"""
    games = db.getAllGames()
    return flask.render_template("allGames.html", games=games)


@gamelist.route("/game/<game>", endpoint="game", methods=["GET"])
def game(game):
    """Send a specific game page"""
    # url decode game
    game = db.getGameByName(game)
    if game is None:
        return flask.render_template("error.html", title="404: Game not found", message="The game you are looking for does not exist."), 404
    return flask.render_template("game.html", **game)


@gamelist.route("/lists", endpoint="lists", methods=["GET"])
def lists():
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


@gamelist.route("/games/add", endpoint="addGameGet", methods=["GET"])
def addGameGet():
    """Send the page for adding a new game"""
    genres = db.getGenres()
    publishers = db.getPublishers()

    return flask.render_template("addGame.html", genres=genres, genreCount=len(genres), publishers=publishers, publisherCount=len(publishers))


@gamelist.route("/games/add", endpoint="addGamePost", methods=["POST"])
def addGamePost():
    """Processes the new game form and adds game to the database"""
    genres = db.getGenres()
    publishers = db.getPublishers()

    gameTitle = flask.request.form["gameName"]
    desc = flask.request.form["desc"]
    releaseDate = flask.request.form["releaseDate"]
    selectedGenres = flask.request.form.getlist("genres")
    selectedPublishers = flask.request.form.getlist("publishers")

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

    db.addGame(gameTitle, desc, releaseDate, selectedGenres, selectedPublishers)

    return flask.redirect(flask.url_for("gamelist.allGames"))


@gamelist.route("/games/addGenre", endpoint="genreAddGet", methods=["GET"])
def genreAddGet():
    """Send the page for adding a new genre"""
    return flask.render_template("addGenre.html")


@gamelist.route("/games/addGenre", endpoint="genreAddPost", methods=["POST"])
def genreAddPost():
    """Processes the new genre form and adds genre to the database"""
    genreName = flask.request.form["genreName"]
    if 3 <= len(genreName) < 32:
        db.addGenre(genreName)
        return flask.redirect(flask.url_for("gamelist.allGames"))
    return flask.render_template("addGenre.html", error="Genre name must be between 3 and 32 characters long.", genreName=genreName)


@gamelist.route("/games/addPublisher", endpoint="publisherAddGet", methods=["GET"])
def publisherAddGet():
    """Send the page for adding a new publisher"""
    return flask.render_template("addPublisher.html")


@gamelist.route("/games/addPublisher", endpoint="publisherAddPost", methods=["POST"])
def publisherAddPost():
    """Processes the new publisher form and adds publisher to the database"""
    publisherName = flask.request.form["publisherName"]
    if 3 <= len(publisherName) < 64:
        db.addPublisher(publisherName)
        return flask.redirect(flask.url_for("gamelist.allGames"))
    return flask.render_template("addPublisher.html", error="Publisher name must be between 3 and 64 characters long.", publisherName=publisherName)
    

if "__main__" == __name__:
    import database
    import validator
    db = database.database("../data/", validator.validator)
