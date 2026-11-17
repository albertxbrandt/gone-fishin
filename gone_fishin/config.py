"""App-wide settings: the window title, how many casts the Fishing Log shows, and where the save file lives."""

import os
import sys

APP_TITLE = "Gone Fishin'"
HISTORY_LIMIT = 10  # casts shown in the Fishing Log


def _app_dir():
    """Folder the save file goes in: next to the .exe when built, or the project folder when run from source."""
    # A --onefile exe unpacks to a temp folder, so keep the database next to the exe itself.
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


DB_PATH = os.path.join(_app_dir(), "fishing.db")
