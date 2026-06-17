import sys
import os
import traceback

sys.path.insert(0, os.path.dirname(__file__))

try:
    from app import app as application
except Exception:
    with open(os.path.join(os.path.dirname(__file__), "passenger_error.log"), "w") as f:
        traceback.print_exc(file=f)
    raise
