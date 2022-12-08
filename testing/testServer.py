#!/usr/bin/env python3

from scripts.database import database
from scripts.validator import validator
import testing.utils

import flask
import hashlib
import os
import sys
import unittest

class serverTests(testing.utils.baseTests):

    @classmethod
    def setUpClass(self):
        super().setUpClass()
        sys.argv = ["server.py", "--data-dir", self.tempDataDir]
        import server
        self.db = server.db
        self.client = server.gamelist.test_client()
        self.client.testing = True

    def testStatic(self):
        """Test accessing static files"""
        response = self.client.get("/static/images/defaultPFP.png")
        self.assertEqual(response.status_code, 200, "Not found")
    
    def testRegisterValid(self):
        """Test registering with valid data"""
        self.client.post("/register", data={
            "username":     "RegisterTest",
            "password":     "TestRegister##123",
            "email":        "test@example.com",
            "dob":          "2003-07-23",
            "phonenumber":  "07000000000"
        })
        self.assertTrue(self.db.getUserByUsername("RegisterTest"), "User not added to database")

    def testRegisterInvalid(self):
        """Test registering with invalid data"""
        validData = {
            "username":     "validUsername",
            "password":     "TestRegister##123",
            "email":        "test2@example.com",
            "dob":          "2003-07-23",
            "phonenumber":  "07000000000"
        }
        for invalidData, reason in (
            ({"username":     "shit"}, 
                b"Username contains profanity"),
            ({"password":     "weakPassword"},
                b"Password must contain at least one uppercase and lowercase letter, one number, and one special character"),
            ({"email":        "notAnEmail.com"}, 
                b"Email is invalid"),
            ({"dob":          "2019-12-01"}, 
                b"You must be at least 13 years old to use this service"),
            ({"phonenumber":  "0118 999 88199 9119 725 3"}, 
                b"Phone number is invalid")
        ):
            data = {**validData, **invalidData}
            response = self.client.post("/register", data=data)
            self.assertIn(reason, response.data, "Error message not in response")
            self.assertFalse(self.db.getUserByUsername(data["username"]), "User added to database")

    def testLoginValid(self):
        """Test logging in with an existing data"""
        self.db.addUser("joe", "Pa55w0rd!123", "test473@example.com",
            "2003-07-23", "07000000000")
        response = self.client.post("/login", data={
            "username": "joe",
            "password": "Pa55w0rd!123"
        })
        self.assertEqual(response.status_code, 302, "Not redirected")
        self.assertEqual(response.location, "/games", "Not redirected to games page")
        self.assertIn(b"Log-Out", self.client.get("/").data, "Not logged in")

    def testLoginInvalid(self):
        """Test logging in with invalid data"""
        self.db.addUser("joe2", "Pa55w0rd!123", "test475@example.com",
            "2003-07-23", "07000000000")
        for response in (
            self.client.post("/login", data={
                "username": "among",
                "password": "Pa55w0rd!123"
            }),
            self.client.post("/login", data={
                "username": "joe2",
                "password": "amogus"
            })
        ):
            self.assertNotIn(b"Log-Out", self.client.get("/").data, "Not logged out")
            self.assertIn(b"<title>Log-in</title>", response.data, "Not on login page")
            self.assertIn(b"Invalid username or password", response.data, "Error message not in response login page")

    def testLogout(self):
        """Test that the user is logged out
        uses the nav bar to know"""
        self.db.addUser("joe3", "Pa55w0rd!123", "test278@example.com",
            "2003-07-23", "07000000000")
        self.client.post("/login", data={
            "username": "joe3",
            "password": "Pa55w0rd!123"
        })
        self.assertIn(b"Log-Out", self.client.get("/").data, "Not logged in")
        self.client.get("/logout")
        self.assertNotIn(b"Log-Out", self.client.get("/").data, "Not logged out")

    def testProfilePictureUpload(self):
        """Test uploading a profile picture"""
        self.db.addUser("joe4", "Pa55w0rd!123", "test999@example.com",
            "2003-07-23", "07000000000")
        self.client.post("/login", data={
            "username": "joe4",
            "password": "Pa55w0rd!123"
        })
        with open("static/images/evil mung.png", "rb") as f:
            response = self.client.post("/images/profile/upload", data={
                "image": (f, "testImage.png")
            })
        self.assertEqual(b"{\"success\":true}\n", response.data, "Not successful")
        filename = self.db.directory + "/images/pfp/" + hashlib.md5(b"joe4").hexdigest() + ".png"
        self.assertTrue(os.path.exists(filename), "File not uploaded")

    def testAddGenre(self):
        """Test adding a genre"""
        self.client.post("/games/addGenre", data={
            "genreName": "TestGenre"
        })
        self.assertIn("TestGenre", self.db.getGenres(), "Genre not added to database")

    def testAddPublisher(self):
        """Test adding a publisher"""
        self.client.post("/games/addPublisher", data={
            "publisherName": "TestPublisher"
        })
        self.assertIn("TestPublisher", self.db.getPublishers(), "Publisher not added to database")

    def testGetGame(self):
        """Test getting a game"""
        self.db.addGenre("Adventure")
        self.db.addPublisher("Infinite Fall")
        self.db.addGame("Night In The Woods", "Gay cat or something idk", "2017-02-21", ["Adventure"], ["Infinite Fall"])
        response = self.client.get("/game/Night In The Woods")
        self.assertIn(b"Night In The Woods", response.data, "Game not found")
        self.assertIn(b"Gay cat or something idk", response.data, "No Description")
        self.assertIn(b"2017-02-21", response.data, "No Release Date")
        self.assertIn(b"Adventure", response.data, "No Genre")
        self.assertIn(b"Infinite Fall", response.data, "No Publisher")

    def testAddGame(self):
        """Test adding a game"""
        self.db.addGenre("Sandbox")
        self.db.addPublisher("Mojang")
        with open("static/images/evil mung.png", "rb") as f:
            request = self.client.post("/games/add", data={
                "gameName": "Minecaft",
                "desc": "A game about munging",
                "releaseDate": "2009-05-17",
                "genres": "Sandbox",
                "publishers": "Mojang",
                "image": (f, "testImage.png")
            })
        self.assertDictContainsSubset({
            "name": "Minecaft",
            "description": "A game about munging",
            "releaseDate": "2009-05-17",
            "genres": ["Sandbox"],
            "developers": ["Mojang"]
            }, self.db.getGameByName("Minecaft"), 
            "Game not added to database")


if __name__ == "__main__":
    unittest.main()
