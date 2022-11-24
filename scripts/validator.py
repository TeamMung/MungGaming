#!/usr/bin/env python3

from profanity import profanity
import re

class validator:
    """All functions return a tuple of (bool, str).
    The bool is True or False for if the validation passed,
    and the reason it failed validation, or None if it passed."""

    alphanumericRegex = re.compile("^\w+$")

    def __init__(self, db):
        """Set up validation"""
        self.db = db

    def username(self, username):
        """Check if a username is valid."""
        if len(username) > 16 or len(username) < 3:
            return False, "Username must be between 3 and 16 characters long"
        if not self.alphanumericRegex.match(username):
            return False, "Username must be alphanumeric"
        if profanity.contains_profanity(username):
            return False, "Username contains profanity"
        if self.db.getUserByUsername(username):
            return False, "Username already exists"
        return True, None


if __name__ == "__main__":
    import database
    database.database("../data/", validator)

