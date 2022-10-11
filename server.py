#!/usr/bin/env python3

import flask
import sys

gamelist = flask.Flask(__name__)
gamelist.url_map.strict_slashes = False


@gamelist.route("/", methods=["GET"])
def sendIndex():
    return "Hello, world!"


if __name__ == "__main__":
    if "--help" in sys.argv:
        print("Team Mung's Game List Server")
        print("Usage: ./server.py [options]")
        print("Options:")
        print("  --help            Display this help and exit")
        print("  --host HOST       Set the servers host IP")
        print("  --port PORT       Set the servers port")
        print("  --werkzeug        Use werkzeug instead of waitress")
        exit()

    # Get host and port from argv or use the defaults
    host = "0.0.0.0"
    port = 80
    if "--host" in sys.argv:
        host = sys.argv[sys.argv.index("--host") + 1]
    if "--port" in sys.argv:
        port = sys.argv[sys.argv.index("--port") + 1]

    # Use waitress as the WSGI server if it is installed,
    # but use built-in if it isnt, or if --werkzeug argument.
    useWaitress = False
    if not "--werkzeug" in sys.argv:
        try:
            import waitress
            useWaitress = True
        except:
            print("Waitress is not installed, using built-in WSGI server (werkzeug).")

    # Run server
    if useWaitress:
        waitress.serve(gamelist, host=host, port=port)
    else:
        gamelist.run(host=host, port=port)

