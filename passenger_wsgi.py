import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask
application = Flask(__name__)

# Try to load the real app, fall back to debug
_real_app = None
try:
    from app import app
    _real_app = app
except Exception as e:
    pass

@application.route("/")
def index():
    if _real_app:
        return _real_app.view_functions.get("index", lambda: "no index route")()
    return f"<pre>Import failed: {e}\nPython: {sys.version}</pre>"

# If main app loaded, use it
if _real_app:
    application = _real_app
