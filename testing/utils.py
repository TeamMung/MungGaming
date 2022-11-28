import random
import os
import shutil
import unittest

class baseTests(unittest.TestCase):
    def setUp(self):
        """Create temporary directory."""
        tempDataDir = "TeamMungTesting" + str(random.randint(10**7,10**8-1))

        if os.name == "posix":
            self.tempDataDir = "/tmp/" + tempDataDir + "/"
        else:
            self.tempDataDir = "./" + tempDataDir + "/"
        os.makedirs(self.tempDataDir, exist_ok=True)

    def tearDown(self):
        """Remove temporary directory for each set of tests."""
        shutil.rmtree(self.tempDataDir)
