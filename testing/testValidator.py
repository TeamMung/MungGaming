#!/usr/bin/env python3

from scripts.validator import validator
from scripts.database  import database
from testing.utils     import baseTests

import unittest


class validatorTests(baseTests):
    """Set up the validator tests"""

    def setUp(self):
        """Set up the validator tests"""
        super().setUp()
        self.db = database(self.tempDataDir, validator)
        self.validator = self.db.validator
        

class usernameTests(validatorTests):
    """Test the username method"""

    def setUp(self):
        """Create database tables"""
        super().setUp()
        self.db.executeScript("databaseStructure.sql")

    def validInvalid(self, valid, invalid, message):
        """Test two arrays of valid and invalid usernames"""
        for username in valid:
            self.assertEqual(self.validator.username(username), (True, None))
        for username in invalid:
            self.assertEqual(self.validator.username(username), (False, message))
    
    def testLength(self):
        """Test the length of the username"""
        message = "Username must be between 3 and 16 characters long"
        for i in (*range(0, 3), 17, 20, 128):
            self.assertEqual(self.validator.username("a" * i), (False, message))
        for i in range(3, 17):
            self.assertEqual(self.validator.username("a" * i), (True, None))
    
    def testAlphaNumeric(self):
        """Test the username for alpha-numeric characters"""
        valid = ["JoeMung", "bigfloppa", "big_chungus_sus", "Amogus1337", "poggers"]
        invalid = ["Bruh Hi", "#floppa", "among us 𐐘", "💀💀💀💀💀💀", "👁👄👁"]
        message = "Username must be alphanumeric"
        self.validInvalid(valid, invalid, message)
    
    def testProfanity(self):
        """Test if the username contains profanity"""
        valid = ["Munger", "CHUNGUS", "bruh"]
        invalid = ["shit", "you_fucking_mung", "faggot"]
        message = "Username contains profanity"
        self.validInvalid(valid, invalid, message)

    def testDoesntExist(self):
        """Add user to database and test if username exists"""
        print("hi")
        self.assertEqual(self.validator.username("test1"), (True, None))
        self.assertEqual(self.validator.username("test2"), (True, None))
        
        self.db.addUser("test1", "Mung", "test@example.com", "20/04/1987", "07123456789")

        self.assertEqual(self.validator.username("test1"), (False, "Username already exists"))
        self.assertEqual(self.validator.username("test2"), (True, None))

if __name__ == "__main__":
    unittest.main()
