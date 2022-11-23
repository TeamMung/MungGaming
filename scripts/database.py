#!/usr/bin/env python3

import bcrypt
import os
import sqlite3

class database:
    def __init__(self, directory="data"):
        """Set up database."""
        self.directory = directory
        self.filename = os.path.join(self.directory, "database.db")
        os.makedirs(self.directory, exist_ok=True)

    def connect(self):
        """Access the database."""
        con = sqlite3.connect(self.filename)
        cur = con.cursor()
        return con, cur

    def executeScript(self, filename):
        """Execute a script file."""
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

    def getUser(self, username):
        """Get a user from the database."""
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
            WHERE users.username = ?", (username,))
        user = cur.fetchone()
        con.close()
        return {
            "username":     user[0],
            "passwordHash": user[1],
            "email":        user[2],
            "dateOfBirth":  user[3],
            "phoneNumber":  user[4],
            "role": user[5]
        }

    def checkPassword(self, username, password):
        """Check if a password is correct for a user."""
        user = self.getUser(username)
        if user is None:
            return False
        password = password.encode("utf-8")
        passwordHash = user["passwordHash"]
        return bcrypt.checkpw(password, passwordHash)
    
    def changeUserRole(self, username, role):
        """Change a user's role."""
        con, cur = self.connect()
        cur.execute(
            "UPDATE users SET roleID = (\
                (SELECT roleID from userRoles WHERE role = ?) \
            ) WHERE username = ?", (role, username))
        con.commit()
        con.close()


if __name__ == "__main__":
    db = database(os.path.join(os.path.dirname(__file__), "../data/"))
    db.executeScript("databaseStructure.sql")
