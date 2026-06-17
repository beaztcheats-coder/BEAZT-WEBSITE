import sys
import os

# Enable Passenger development mode for detailed errors
os.environ["PASSENGER_APP_ENV"] = "development"
sys.path.insert(0, os.path.dirname(__file__))

# Log startup
try:
    with open(os.path.join(os.path.dirname(__file__), "startup.log"), "w") as f:
        f.write(f"Python: {sys.version}\n")
        f.write(f"Path: {sys.path}\n")
        f.write(f"Files in dir: {os.listdir(os.path.dirname(__file__))}\n")
except Exception:
    pass

from app import app as application
