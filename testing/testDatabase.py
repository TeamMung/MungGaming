#!/usr/bin/env python3

from scripts.validator import validator
from scripts.database import database
from testing.utils import baseTests

import unittest

class databaseTests(baseTests):
    def setUp(self):
        super().setUp()
        self.db = database(self.tempDataDir, validator)
        self.db.executeScript("databaseStructure.sql")

    def testTablesExist(self):
        tables = self.db.executeQuery("SELECT name FROM sqlite_master WHERE type='table'", ())
        for tablename in ["users", "userRoles", "games", "gameImages", "gameReviews", "gameLists", "gameListLink", "gameGenres", "gameGenresLink", "gamePublishers", "gamePublishersLink"]:
            self.assertIn((tablename,), tables)

    def testUsers(self):
        self.db.addUser("TestUser", "TestPassword", "TestEmail@example.com",
                        "2003-07-23", "07777777777")
        self.assertDictContainsSubset({
            "username": "TestUser",
            "email": "TestEmail@example.com",
            "dateOfBirth": "2003-07-23",
            "phoneNumber": "07777777777",
            "role": "user"
        }, self.db.getUserByUsername("TestUser"))
        self.assertEqual(self.db.getUserByUsername("TestUser"),
                         self.db.getUserByEmail("TestEmail@example.com"))
        self.db.changeUserRole("TestUser", "admin")
        self.assertEqual(self.db.getUserByUsername("TestUser")["role"], "admin")
        self.assertTrue(self.db.checkPassword("TestUser", "TestPassword"))
        self.assertFalse(self.db.checkPassword("TestUser", "WrongPassword"))

if __name__ == "__main__":
    unittest.main()