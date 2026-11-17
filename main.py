"""Gone Fishin' entry point: set up the save file, open the window, and close the database on exit.

Project layout:
  gone_fishin/data   backend storage, the only code that talks to SQLite
  gone_fishin/logic  backend game rules and story text (no UI code)
  gone_fishin/ui     frontend Tkinter window (no game rules or SQL)
"""

from gone_fishin.data import database
from gone_fishin.logic.game import Game
from gone_fishin.ui.app import App


def main():
    database.init_db()
    try:
        App(Game()).mainloop()  # runs until the window is closed
    finally:
        database.close()


if __name__ == "__main__":
    main()
