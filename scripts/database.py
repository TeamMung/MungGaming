#!/usr/bin/env python3

import bcrypt
import os
import sqlite3

class database:
    def __init__(self, directory, validator):
        """Set up database."""
        self.directory = directory
        self.filename = os.path.join(self.directory, "database.db")
        os.makedirs(os.path.join(self.directory, "images/pfp"), exist_ok=True)
        self.validator = validator(self)

    def connect(self):
        """Access the database."""
        con = sqlite3.connect(self.filename)
        cur = con.cursor()
        return con, cur

    def executeScript(self, filename):
        """Execute a script file.
        
        Keyword arguments:
        filename -- the name of the sql file to execute"""
        with open(os.path.join(os.path.dirname(__file__), filename), "r") as f:
            script = f.read()
        con, cur = self.connect()
        cur.executescript(script)
        con.commit()
        con.close()

    def executeQuery(self, query, params):
        """Execute a query and return the result.
        
        Keyword arguments:
        query  -- the query to execute
        params -- the parameters to pass to the query"""
        con, cur = self.connect()
        cur.execute(query, params)
        results = cur.fetchall()
        con.close()
        return results

    def addUser(self, username, password, email, dateOfBirth, phoneNumber):
        """Add a user to the database.
        
        The password will be hashed using BCrypt.
        The user will be given a default role of user."""
        salt = bcrypt.gensalt()
        password = password.encode("utf-8")
        passwordHash = bcrypt.hashpw(password, salt)
        con, cur = self.connect()
        cur.execute(
            "INSERT INTO users (\
                roleID, \
                username, \
                passwordHash, \
                email, \
                dateOfBirth, \
                phoneNumber \
            ) VALUES (\
                (SELECT roleID from userRoles WHERE role = 'user'), \
                ?, ?, ?, ?, ?)",
            (username, passwordHash, email, dateOfBirth, phoneNumber))
        con.commit()
        con.close()


    def getUser(self, where, value):
        """Get a user from the database.
        Returns a dictionary of the user's details,
        or None if the user does not exist.
        Used by getUserByUsername and getUserByEmail to avoid code duplication.
        Do not use this function directly."""
        con, cur = self.connect()
        cur.execute(
            "SELECT \
                users.username, \
                users.passwordHash, \
                users.email, \
                users.dateOfBirth, \
                users.phoneNumber, \
                userRoles.role \
            FROM users \
            INNER JOIN userRoles ON users.roleID = userRoles.roleID \
            WHERE LOWER(users." + where + ") = ?", (value.lower(),))
        user = cur.fetchone()
        con.close()
        try:
            return {
                "username":     user[0],
                "passwordHash": user[1],
                "email":        user[2],
                "dateOfBirth":  user[3],
                "phoneNumber":  user[4],
                "role": user[5]
            }
        except TypeError:
            return None

    def getUserByUsername(self, username):
        """Get a user from the database by their username.

        Keyword arguments:
        username -- the username of the user to get"""
        return self.getUser("username", username)

    def getUserByEmail(self, email):
        """Get a user from the database by their email.

        Keyword arguments:
        email -- the email of the user to get"""
        return self.getUser("email", email)

    def checkPassword(self, username, password):
        """Check if a password is correct for a user.
        Returns True if the password is correct, False if not.
        
        Keyword arguments:
        username -- the username of the user to check
        password -- the password to check"""
        user = self.getUserByUsername(username)
        if user is None:
            return False
        password = password.encode("utf-8")
        passwordHash = user["passwordHash"]
        return bcrypt.checkpw(password, passwordHash)
    
    def changeUserRole(self, username, role):
        """Change a user's role.
        
        Keyword arguments:
        username -- the username of the user to change
        role     -- the new role of the user"""
        con, cur = self.connect()
        cur.execute(
            "UPDATE users SET roleID = (\
                (SELECT roleID from userRoles WHERE role = ?) \
            ) WHERE LOWER(username) = ?", (role, username.lower()))
        con.commit()
        con.close()

    def addGame(self, name, description, releaseDate, genres, publishers):
        """Add a game to the database.
        Will not add genres or publishers that do not already exist.
        
        Keyword arguments:
        name        -- the name of the game
        description -- the description of the game
        releaseDate -- the release date of the game
        genres      -- an array of the genres of the game
        publishers  -- an array of developers and publishers of the game"""
        con, cur = self.connect()
        cur.execute(
            "INSERT INTO games (gameName, gameDescription, releaseDate, approved) VALUES (?, ?, ?, 0)",
            (name, description, releaseDate))
        gameID = cur.lastrowid
        for genre in genres:
            cur.execute("SELECT genreID from gameGenres WHERE LOWER(genre) = ?", (genre.lower(),))
            genreID = cur.fetchone()
            if genreID is not None:
                genreID = genreID[0]
                cur.execute("INSERT INTO gameGenresLink (gameID, genreID) VALUES (?, ?)", (gameID, genreID))
        for publisher in publishers:
            cur.execute("SELECT publisherID from gamePublishers WHERE LOWER(publisherName) = ?", (publisher.lower(),))
            publisherID = cur.fetchone()
            if publisherID is not None:
                publisherID = publisherID[0]
                cur.execute("INSERT INTO gamePublishersLink (gameID, publisherID) VALUES (?, ?)", (gameID, publisherID))
        con.commit()
        con.close()

    def unConcat(self, string):
        """Split group_concat into an array.
        
        Keyword arguments:
        string -- the string to remove the trailing comma from"""
        if string is None:
            return []
        return string.split(",")

    def getGame(self, where, value):
        """Get a game from the database.
        Will have arrays of genres and publishers/developers.
        Use getGameByName or getGameByID instead of this function.

        Keyword arguments:
        where -- what to get the game by
        value -- the value to get the game by"""
        con, cur = self.connect()
        cur.execute(
            "SELECT \
                games.gameID, \
                games.approved, \
                games.gameName, \
                games.gameDescription, \
                games.releaseDate, \
                GROUP_CONCAT(DISTINCT g.genre), \
                GROUP_CONCAT(DISTINCT p.publisherName) \
            FROM games \
            LEFT OUTER JOIN gameGenresLink gl     ON games.gameID = gl.gameID \
            LEFT OUTER JOIN gameGenres g          ON gl.genreID = g.genreID \
            LEFT OUTER JOIN gamePublishersLink pl ON games.gameID = pl.gameID \
            LEFT OUTER JOIN gamePublishers p      ON pl.publisherID = p.publisherID \
            WHERE " + where + " = ? ", (value,))
        game = cur.fetchone()
        con.close()
        if game[0] is not None:
            return {
                "gameID":       game[0],
                "approved":     bool(game[1]),
                "name":         game[2],
                "description":  game[3],
                "releaseDate":  game[4],
                "genres":       self.unConcat(game[5]),
                "developers":   self.unConcat(game[6])
            }
        return None

    def getGameByName(self, name):
        """Get a game from the database by its name.
        Will have arrays of genres and publishers/developers.
        
        Keyword arguments:
        name -- the name of the game to get"""
        return self.getGame("LOWER(games.gameName)", name.lower())

    def getGameByID(self, gameID):
        """Get a game from the database by its ID.
        Will have arrays of genres and publishers/developers.
        
        Keyword arguments:
        gameID -- the ID of the game to get"""
        return self.getGame("games.gameID", gameID)

    def getAllGames(self):
        """Get an array of all game titles in the database."""
        con, cur = self.connect()
        cur.execute("SELECT gameName FROM games")
        games = cur.fetchall()
        con.close()
        return [game[0] for game in games]

    def deleteGameByID(self, id):
        """Delete a game from the database by its name.
        
        Keyword arguments:
        id -- the id of the game to delete"""
        con, cur = self.connect()
        cur.execute(
            "DELETE FROM games WHERE gameID = ?", (id,))
        con.commit()
        con.close()

    def addGenre(self, genre):
        """Add a genre to the database.
        
        Keyword arguments:
        genre -- the genre to add"""
        con, cur = self.connect()
        cur.execute(
            "INSERT INTO gameGenres (genre) VALUES (?)", (genre,))
        con.commit()
        con.close()

    def addPublisher(self, publisher):
        """Add a publisher to the database.
        
        Keyword arguments:
        publisher -- the publisher to add"""
        con, cur = self.connect()
        cur.execute(
            "INSERT INTO gamePublishers (publisherName) VALUES (?)", (publisher,))
        con.commit()
        con.close()

    def getGenres(self):
        """Get all genres from the database."""
        con, cur = self.connect()
        cur.execute(
            "SELECT genre FROM gameGenres")
        genres = cur.fetchall()
        con.close()
        return [genre[0] for genre in genres]

    def getPublishers(self):
        """Get all publishers from the database."""
        con, cur = self.connect()
        cur.execute(
            "SELECT publisherName FROM gamePublishers")
        publishers = cur.fetchall()
        con.close()
        return [publisher[0] for publisher in publishers]

    def deleteGenre(self, genre):
        """Delete a genre from the database.
        
        Keyword arguments:
        genre -- the genre to delete"""
        con, cur = self.connect()
        cur.execute(
            "DELETE FROM gameGenres WHERE genre = ?", (genre,))
        con.commit()
        con.close()

    def deletePublisher(self, publisher):
        """Delete a publisher from the database.
        
        Keyword arguments:
        publisher -- the publisher to delete"""
        con, cur = self.connect()
        cur.execute(
            "DELETE FROM gamePublishers WHERE publisherName = ?", (publisher,))
        con.commit()
        con.close()

if __name__ == "__main__":
    from validator import validator
    db = database(os.path.join(os.path.dirname(__file__), "../data/"), validator)
    db.executeScript("databaseStructure.sql")
