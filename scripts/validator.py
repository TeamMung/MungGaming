#!/usr/bin/env python3

import datetime
from profanity import profanity
import re

class validator:
    """All functions return a tuple of (bool, str).
    The bool is True or False for if the validation passed,
    and the reason it failed validation, or None if it passed."""

    def __init__(self, db):
        """Set up validation"""
        self.db = db

    def username(self, username):
        """Check if a username is valid."""
        if len(username) > 16 or len(username) < 3:
            return False, "Username must be between 3 and 16 characters long"
        if not re.match("^\w+$", username):
            return False, "Username must be alphanumeric"
        if profanity.contains_profanity(username):
            return False, "Username contains profanity"
        if self.db.getUserByUsername(username):
            return False, "Username already exists"
        return True, None

    def password(self, password):
        """Check if a password is valid."""
        if len(password) > 64 or len(password) < 8:
            return False, "Password must be between 8 and 64 characters long"
        if (not re.search("[a-z]", password)
                or not re.search("[A-Z]", password)
                or not re.search("[0-9]", password)
                or not re.search("[^a-zA-Z0-9]", password)):
            return False, "Password must contain at least one uppercase and lowercase letter, one number, and one special character"
        return True, None

    def email(self, email):
        """Check if an email is valid."""
        if not re.match("[a-zA-Z0-9][^@]+[a-zA-Z0-9]@[a-zA-Z0-9\-\.]+\.[a-zA-Z0-9\-\.]+[a-zA-Z0-9]$", email):
            return False, "Email is invalid"
        if self.db.getUserByEmail(email):
            return False, "Email has already been used"
        return True, None

    def dateOfBirth(self, dateOfBirth):
        """Check if a date of birth is:
        in YYYY-MM-DD format
        and is over 13 years old and under 150 years old"""
        if re.match("^\d\d\d\d-\d\d-\d\d$", dateOfBirth):
            try:
                date = datetime.datetime.strptime(dateOfBirth, "%Y-%m-%d")
                if (date > (datetime.datetime.now() - datetime.timedelta(days=365.25*13)).replace(hour=0, minute=0, second=0, microsecond=0)
                    and date < datetime.datetime.now()):
                    return False, "You must be at least 13 years old to use this service"
                if (date > (datetime.datetime.now() - datetime.timedelta(days=365.25*150)) 
                    and date < (datetime.datetime.now() - datetime.timedelta(days=365.25*13))):
                    return True, None
            except ValueError:
                pass
        return False, "Date of birth must be in YYYY-MM-DD format"

    def phoneNumber(self, phoneNumber):
        """Check if a phone number is valid."""
        digitsOnly = phoneNumber.replace(" ", "").replace("-", "").replace("(", "").replace(")", "").replace("+", "")
        if (len(phoneNumber) <= 20 and digitsOnly.isdigit()
            and ((("+" == phoneNumber[0] or "(+" == phoneNumber[:2]) and len(phoneNumber.split("+")) == 2 and 14 > len(digitsOnly) > 11)
                 or ("+" not in phoneNumber and len(digitsOnly) == 11))):
            return True, None
        return False, "Phone number is invalid"

    def gameTitle(self, gameTitle):
        """Check the game title is valid"""
        if len(gameTitle) > 64 or len(gameTitle) < 3:
            return False, "Game title must be between 3 and 64 characters long"
        if self.db.getGameByName(gameTitle):
            return False, "Game already exists"
        return True, None

    def releaseDate(self, releaseDate):
        """Check the release date is valid"""
        if re.match("^\d\d\d\d-\d\d-\d\d$", releaseDate):
            try:
                date = datetime.datetime.strptime(releaseDate, "%Y-%m-%d")
                now = datetime.datetime.now()
                ## if date is more than 1960-01-01
                if date >= datetime.datetime(1960, 1, 1) and date <= now:
                    return True, None
                elif date > now:
                    return False, "Release date must be in the past"
            except ValueError:
                pass
        return False, "Release date must be in YYYY-MM-DD format"


if __name__ == "__main__":
    import database
    database.database("../data/", validator)

