#!/usr/bin/env python3

import flask
import logging
import os
import sys

# Get variables from argv or use the defaults
argv = {}
for arg, var, default in [
    ("--host",      "host",     "0.0.0.0"),
    ("--port",      "port",     "80"),
    ("--data-dir",  "dataDir",  os.path.join(os.path.dirname(__file__), "data"))
]:
    if arg in sys.argv:
        argv[var] =  sys.argv[sys.argv.index(arg) + 1]
    else:
        argv[var] = default

# Set up database
from scripts.database import database
db = database(argv["dataDir"])
db.executeScript("databaseStructure.sql")

# Set up flask
gamelist = flask.Flask(__name__)
gamelist.url_map.strict_slashes = False
import scripts.routes
scripts.routes.db = db
gamelist.register_blueprint(scripts.routes.gamelist)
gamelist.config["TEMPLATES_AUTO_RELOAD"] = True

@gamelist.after_request
def afterRequest(response):
    """Add server to user agent"""
    response.headers["Server"] = f"TeamMungGameList Python/{sys.version.split()[0]}"
    return response

# Use waitress as the WSGI server if it is installed,
# but use built-in if it isnt, or if --werkzeug argument.
useWaitress = False
if not "--werkzeug" in sys.argv:
    try:
        import waitress
        useWaitress = True
    except:
        print("Waitress is not installed, using built-in WSGI server (werkzeug).")

if __name__ == "__main__":
    if "--help" in sys.argv:
        print("Team Mung's Game List Server")
        print("All Rights Reserved Copyright (c) 2022")
        print("Charlottieee, HenryMullins, JoeBlakeB, Thek9cow")
        print("Usage: ./server.py [options]")
        print("Options:")
        print("  --help            Display this help and exit")
        print("  --host HOST       Set the servers host IP")
        print("  --port PORT       Set the servers port")
        print("  --werkzeug        Use werkzeug instead of waitress")
        print("  --data-dir DIR    Set the directory where data is stored")
        exit()

    # Run server
    if useWaitress:
        logging.getLogger("waitress.queue").setLevel(logging.CRITICAL)
        waitress.serve(gamelist, host=argv["host"], port=argv["port"], threads=8)
    else:
        gamelist.run(host=argv["host"], port=argv["port"])

