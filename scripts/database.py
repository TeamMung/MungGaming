#!/usr/bin/env python3

import bcrypt
import os
import sqlite3

class database:
    def __init__(self, directory, validator):
        """Set up database."""
        self.directory = directory
        self.filename = os.path.join(self.directory, "database.db")
        os.makedirs(self.directory, exist_ok=True)
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


if __name__ == "__main__":
    from validator import validator
    db = database(os.path.join(os.path.dirname(__file__), "../data/"), validator)
    db.executeScript("databaseStructure.sql")
