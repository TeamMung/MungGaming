# Team Mung's Game List

Team Mung's Game List Website.

## Team Members

<table>
<tr>
<td align="center"><a href="https://github.com/charlottieee"><img src="https://avatars.githubusercontent.com/u/105317117?v=4" width="128px;" alt=""/><br /><sub><b>Charlotte Beale</b></sub></a><br /></td>
<td align="center"><a href="https://github.com/thek9cow"><img src="https://avatars.githubusercontent.com/u/91023673?v=4" width="128px;" alt=""/><br /><sub><b>Chris Topp</b></sub></a><br /></td>
<td align="center"><a href="https://github.com/HenryMullins"><img src="https://avatars.githubusercontent.com/u/90117117?v=4" width="128px;" alt=""/><br /><sub><b>Henry Mullins</b></sub></a><br /></td>
<td align="center"><a href="https://github.com/JoeBlakeB"><img src="https://avatars.githubusercontent.com/u/34925002?v=4" width="128px;" alt=""/><br /><sub><b>Joe Baker</b></sub></a><br /></td>
</tr>
<table>

## Usage

To start the server run:

`./server.py` on linux or `python server.py` on windows

To stop the server send a KeyboardInterrupt signal (ctrl + C).

The default host is `0.0.0.0` and port is `80` and you can change it with the `--host` and `-port`:

`./server.py --host 127.0.0.1 --port 8080`

Data is stored in `./data` and this can be changed with `--data-dir`:

`./server.py --data-dir /path/to/data/directory/`

By default waitress will be used as the WSGI if it is installed and will use werkzeug (the built-in WSGI) if it isn't. To force the server to only use werkzeug add the `--werkzeug` argument:

`./server.py --werkzeug`

And to run the unit tests run:

`python3 -m unittest discover testing`

## Dependencies

Python 3.7+, all packages are listed in `requirements.txt`

To install them all, run `python3 -m pip install -r requirements.txt`

## Misc

- Copyright © Charlotte Beale (charlottieee), Chris Topp (thek9cow), Henry Mullins (HenryMullins), Joe Baker (JoeBlakeB), All Rights Reserved
- Server tested with Python 3.10.7 on Linux
