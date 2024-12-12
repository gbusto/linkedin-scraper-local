# Overview

Instructions on how to set this up and run it.

## Setup

1. Clone the repo
2. Create a virtual environment (`python -m venv .venv`)
3. Activate the virtual environment (`source .venv/bin/activate`)
4. Install the dependencies (`pip install -r requirements.txt`)
5. Install playwright (`playwright install`)
6. We need to run `li_login.py` once to open playwright browser, log into linked in, and save the session data.
7. Run `main.py` to start the script.

Exmaple:
```
python li_login.py
# Log in to linked in and then close the browser window.
```

Then,
```
python main.py --handle alexxubyte --scrolls 10 --output-dir ./
```

And you should see a JSON and CSV output file that you can use.

By default, it'll scroll down 50 times, but in the test example I only have it scroll down 10 times.

Basically, we programmatically open a browser window with a logged in linked in session, go to someone's activity page, scroll down a bunch of times to load posts, and then extract the posts.

Feel free to scroll 100 times or 1000 times, it'll load more posts. But I'm not sure if it'll trigger any security measures by linked in if you do it too many times in a row.