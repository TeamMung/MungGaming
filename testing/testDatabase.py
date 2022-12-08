#!/usr/bin/env python3

from scripts.validator import validator
from scripts.database import database
from testing.utils import baseTests

import unittest

class databaseTests(baseTests):

    @classmethod
    def setUpClass(self):
        super().setUpClass()
        self.db = database(self.tempDataDir, validator)
        self.db.executeScript("databaseStructure.sql")

class structureTests(databaseTests):
    def testTablesExist(self):
        """Test that the tables exist."""
        tables = self.db.executeQuery("SELECT name FROM sqlite_master WHERE type='table'", ())
        for tablename in ["users", "userRoles", "games", "gameImages", "gameReviews", "gameLists", "gameListLink", "gameGenres", "gameGenresLink", "gamePublishers", "gamePublishersLink"]:
            self.assertIn((tablename,), tables)

class userTests(databaseTests):

    @classmethod
    def setUpClass(self):
        """Add user to test with."""
        super().setUpClass()
        self.db.addUser("TestUser", "Pa55word!", "TestEmail@example.com",
                        "2003-07-23", "07777777777")

    def testGetUser(self):
        self.assertDictContainsSubset({
            "username": "TestUser",
            "email": "TestEmail@example.com",
            "dateOfBirth": "2003-07-23",
            "phoneNumber": "07777777777",
            "role": "user"
        }, self.db.getUserByUsername("TestUser"))
        self.assertEqual(self.db.getUserByUsername("TestUser"),
                         self.db.getUserByEmail("TestEmail@example.com"))
    
    def testChangeRoles(self):
        self.db.changeUserRole("TestUser", "admin")
        self.assertEqual(self.db.getUserByUsername("TestUser")["role"], "admin")
        self.db.changeUserRole("TestUser", "user")
        self.assertEqual(self.db.getUserByUsername("TestUser")["role"], "user")
    
    def testPassword(self):
        self.assertTrue(self.db.checkPassword("TestUser", "Pa55word!"))
        self.assertFalse(self.db.checkPassword("TestUser", "Mung1!sus"))

class gameTests(databaseTests):
    game = ["Night In The Woods",
            "College dropout Mae Borowski returns home to the crumbling former mining town of Possum Springs seeking to resume her aimless former life and reconnect with the friends she left behind. But things aren't the same. Home seems different now and her friends have grown and changed. Leaves are falling and the wind is growing colder. Strange things are happening as the light fades.",
            "2017-02-21",
            ["Adventure", "Indie"],
            ["Infinite Fall", "Finji"]]

    def testGameOnItsOwn(self):
        """Test adding a game with the genres publishers not existing.
        Then delete the game."""
        self.db.addGame(*self.game)
        getGame = self.db.getGameByName(self.game[0])
        self.assertDictContainsSubset({
            "name": self.game[0],
            "approved": False,
            "description": self.game[1],
            "releaseDate": self.game[2],
            "genres": [],
            "developers": []
        }, getGame)
        self.assertEqual(self.db.getGameByID(getGame["gameID"]), getGame)
        self.db.deleteGameByID(getGame["gameID"])
        self.assertIsNone(self.db.getGameByName(self.game[0]))

    def testGameWithGenresAndPublishers(self):
        """Test a game with genres and publishers that already exist."""
        self.db.addGenre("Adventure")
        self.db.addGenre("Indie")
        self.db.addPublisher("Infinite Fall")
        self.db.addPublisher("Finji")
        self.db.addGame(*self.game)
        getGame = self.db.getGameByName(self.game[0])
        self.assertDictContainsSubset({
            "name": self.game[0],
            "approved": False,
            "description": self.game[1],
            "releaseDate": self.game[2],
            "genres": self.game[3],
            "developers": self.game[4]
        }, getGame)
        self.assertEqual(self.db.getGameByID(getGame["gameID"]), getGame)
        self.db.deleteGameByID(getGame["gameID"])
        self.db.deleteGenre("Adventure")
        self.db.deleteGenre("Indie")
        self.db.deletePublisher("Infinite Fall")
        self.db.deletePublisher("Finji")
        self.assertIsNone(self.db.getGameByName(self.game[0]))
    
    def adGetDeleteTest(self, values, add, delete, get):
        """Used by the genre and publisher tests"""
        add(values[0])
        self.assertEqual(get(), [values[0]])
        delete(values[0])
        self.assertEqual(get(), [])
        for value in values:
            add(value)
        self.assertEqual(get(), values)
        delete(values[1])
        self.assertEqual(get(), [values[0], values[2]])

    def testGenres(self):
        """Test adding, getting, and deleting game genres"""
        self.adGetDeleteTest(["Horror", "Adventure", "Indie"],
            self.db.addGenre,
            self.db.deleteGenre,
            self.db.getGenres)
    
    def testPublishers(self):
        """Test adding, getting, and deleting game publishers"""
        self.adGetDeleteTest(["Mungjang", "Mungstar", "Mungrosoft"],
            self.db.addPublisher,
            self.db.deletePublisher,
            self.db.getPublishers)

if __name__ == "__main__":
    unittest.main()