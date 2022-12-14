#!/usr/bin/env python3

from scripts.validator import validator
from scripts.database  import database
from testing.utils     import baseTests

import datetime
import unittest


class validatorTests(baseTests):
    """Methods used by multiple tests"""

    dateYearsAgo = lambda self, years: (datetime.date.today() - datetime.timedelta(days=years*365.25)).strftime("%Y-%m-%d")

    @classmethod
    def setUpClass(self):
        """Set up the validator tests"""
        super().setUpClass()
        self.db = database(self.tempDataDir, validator)
        self.validator = self.db.validator

    def length(self, message, valid, invalid, requiredChars=""):
        """Test two arrays of valid and invalid lengths"""
        for length in valid:
            self.assertEqual(self.method(requiredChars + "a" * length), (True, None))
        for length in invalid:
            self.assertEqual(self.method(requiredChars + "a" * length), (False, message))
    
    def validInvalid(self, message, valid, invalid):
        """Test two arrays of valid and invalid values"""
        for value in valid:
            self.assertEqual(self.method(value), (True, None))
        for value in invalid:
            self.assertEqual(self.method(value), (False, message))

    def doesntExist(self, message, value1, value2, addMethod, addValue):
        """Test method, add value to database, then test method again"""
        self.assertEqual(self.method(value1), (True, None))
        self.assertEqual(self.method(value2), (True, None))
        addMethod(*addValue)
        self.assertEqual(self.method(value1), (False, message))
        self.assertEqual(self.method(value2), (True, None))
        

class usernameTests(validatorTests):
    """Test the username method"""

    @classmethod
    def setUpClass(self):
        super().setUpClass()
        self.db.executeScript("databaseStructure.sql")
        self.method = self.validator.username
    
    def testLength(self):
        """Test the length of the username"""
        self.length("Username must be between 3 and 16 characters long",
            range(3, 17), (*range(0, 3), 17, 20, 128))
    
    def testAlphaNumeric(self):
        """Test the username for alpha-numeric characters"""
        self.validInvalid("Username must be alphanumeric",
            ["JoeMung", "bigfloppa", "big_chungus_sus", "Amogus1337", "poggers"], 
            ["Bruh Hi", "#floppa", "among us ????", "????????????????????????", "????????????"])
    
    def testProfanity(self):
        """Test if the username contains profanity"""
        self.validInvalid("Username contains profanity",
            ["Munger", "CHUNGUS", "bruh"],
            ["shit", "you_fucking_mung", "faggot"])

    def testDoesntExist(self):
        """Add user to database and test if username exists"""
        self.doesntExist("Username already exists", "test1", "test2",
            self.db.addUser,
            ("test1", "Mung", "test@example.com", "14/11/1987", "07123456789"))


class passwordTests(validatorTests):
    """Test the password validator method"""

    @classmethod
    def setUpClass(self):
        super().setUpClass()
        self.method = self.validator.password

    def testLength(self):
        """Test the length of the password"""
        self.length("Password must be between 8 and 64 characters long",
            range(4, 61), (*range(0, 4), 61, 62, 69, 85, 128), "aA1#")
    
    def testRequiredChars(self):
        """Test the password for required characters"""
        self.validInvalid("Password must contain at least one uppercase and lowercase letter, one number, and one special character",
            ["Pas55w0rd!", "AmOnGUs1337!", "Mun9er!!", "Password123!", "WhyDidYouKillBigChungus???WeKnowYoureTheImposter!11!!", "Gnk*99vjauwd!$A@"],
            ["pa55w0rd!", "HELLO:FLOPPAWAVE~2:", "#AmongUs", "Password123"])

    
class emailTests(validatorTests):
    """Test the email validator method"""

    @classmethod
    def setUpClass(self):
        super().setUpClass()
        self.db.executeScript("databaseStructure.sql")
        self.method = self.validator.email

    def testValid(self):
        """Test email against some examples"""
        self.validInvalid("Email is invalid",
            ["example@gmail.com", "amon.gus@google.com", "s5411045@bournemouth.ac.uk", "amongus+sus@bing.com", "telly-license@gov.uk"],
            ["@example.com", "amongus.com", "chungus@", "hello@hicom", "email@exampe.com (sus)", "Big Chungus <email@example.com>", ".email@example.com"])

    def testDoesntExist(self):
        """Add user to database and test if username exists"""
        self.doesntExist("Email has already been used",
            "test1@example.com", "test2@example.com",
            self.db.addUser,
            ("test1", "Mung", "test1@example.com", "14/11/1987", "07123456789"))


class dateOfBirthTests(validatorTests):
    """Test the date of birth validator method"""

    @classmethod
    def setUpClass(self):
        super().setUpClass()
        self.method = self.validator.dateOfBirth

    def testValidFormat(self):
        """Test date of birth format"""
        self.validInvalid("Date of birth must be in YYYY-MM-DD format",
            ["2003-07-23", "1994-04-19", "1987-11-14", "1954-06-07", "1912-06-23", "2000-01-01", "2000-12-31"],
            ["2003-7-23", "19/04/1994", "1987-14-11", "54-06-07", "12-06-23", "2000 1 1", "31st December 2000",
             "2003-07-23 16:06:00", "12003-07-23", "23072003", "2003/07/23"])
    
    def testValidAge(self):
        """Test date of birth age"""
        dateYearsAgo = self.dateYearsAgo
        self.validInvalid("You must be at least 13 years old to use this service",
            [dateYearsAgo(13),  dateYearsAgo(13.5), dateYearsAgo(14), dateYearsAgo(18),  dateYearsAgo(20),
             dateYearsAgo(50),  dateYearsAgo(75),   dateYearsAgo(99), dateYearsAgo(100), dateYearsAgo(101)],
            [dateYearsAgo(0),   dateYearsAgo(3),    dateYearsAgo(9),  dateYearsAgo(12),  dateYearsAgo(12.5)])
        # Assumes that date is in wrong format if it is in the future or older than 150 years old
        self.validInvalid("Date of birth must be in YYYY-MM-DD format", [],
            [dateYearsAgo(-1), dateYearsAgo(-2),  dateYearsAgo(-5),  dateYearsAgo(-10), dateYearsAgo(-200),
            dateYearsAgo(151), dateYearsAgo(200), dateYearsAgo(500), dateYearsAgo(750)])


class phoneNumberTests(validatorTests):
    """Test the phone number validator method"""

    @classmethod
    def setUpClass(self):
        super().setUpClass()
        self.method = self.validator.phoneNumber

    def testLocal(self):
        """Test phone number no area code"""
        self.validInvalid("Phone number is invalid",
            ["07123456789", "07987654321", "07777777777", "07888888888", "07444444444", "07555555555", "07123-456-789", "07123 456 789"],
            ["0712345678", "071234567890", "0712345678a", "0712345678!", "0712345678#", "0712345678 ", "07123-456-78", "07000---000"])
    
    def testAreaCode(self):
        """Test phone number with area code"""
        self.validInvalid("Phone number is invalid",
            ["+447123456789", "+447987654321", "+447777777777", "+447888888888", "(+44)7123-456-789", "+44 07123-456-789", "+44 7123-456-789", "+447123 456 789"],
            ["+44712345678", "+44071234567890", "+44712345678a", "+44712345678!", "+44712345678#", "+44712345678 ", "+447123-456-78", "+44700666"])


class gameTitleTests(validatorTests):
    """Test the game title validator method"""

    @classmethod
    def setUpClass(self):
        super().setUpClass()
        self.db.executeScript("databaseStructure.sql")
        self.method = self.validator.gameTitle
    
    def testLength(self):
        """Test the length of the game title"""
        self.length("Game title must be between 3 and 64 characters long",
            range(3, 65), (0, 1, 2, 365, 65, 66, 69, 85, 128))
    
    def testExists(self):
        """Test if game title exists"""
        self.doesntExist("Game already exists",
            "Among Us", "Minecraft", self.db.addGame,
            ("Among Us", "When the imposter is sus", "2018-06-15", [], []))


class releaseDateTests(validatorTests):
    """Test the release date validator method"""

    @classmethod
    def setUpClass(self):
        super().setUpClass()
        self.method = self.validator.releaseDate

    def testValidFormat(self):
        """Test release date format"""
        self.validInvalid("Release date must be in YYYY-MM-DD format",
            ["2003-07-23", "1994-04-19", "1987-11-14", "1964-06-07", "1972-06-23", "2000-01-01", "2000-12-31"],
            ["2003-7-23", "19/04/1994", "1987-14-11", "54-06-07", "12-06-23", "2000 1 1", "31st December 2000",
             "2003-07-23 16:06:00", "12003-07-23", "23072003", "2003/07/23"])

    def testValidAge(self):
        """Test release date age"""
        dateYearsAgo = self.dateYearsAgo
        self.validInvalid("Release date must be in the past",
            [dateYearsAgo(0),   dateYearsAgo(3),    dateYearsAgo(9),  dateYearsAgo(12),  dateYearsAgo(12.5),
             dateYearsAgo(13),  dateYearsAgo(13.5), dateYearsAgo(14), dateYearsAgo(18),  dateYearsAgo(20),
             "2003-07-23", "1994-04-19", "1987-11-14", "1964-06-07", "1972-06-23", "2000-01-01", "2000-12-31",
             "1960-01-01", "1960-12-31", "1960-06-07", "1960-06-23", "1960-04-19", "1960-07-23", "1972-11-29"],
            [dateYearsAgo(-1), dateYearsAgo(-2),  dateYearsAgo(-5),  dateYearsAgo(-10), dateYearsAgo(-200)])
        print("---------------")
        # Assumes that date is in wrong format if it is before the 60s
        self.validInvalid("Release date must be in YYYY-MM-DD format", [],
            [dateYearsAgo(100), dateYearsAgo(151), dateYearsAgo(200), dateYearsAgo(500), dateYearsAgo(750), 
            "1959-12-31", "1959-01-01", "1959-06-07", "1959-06-23", "1959-04-19", "1959-07-23", "1959-11-29"])


if __name__ == "__main__":
    unittest.main()
