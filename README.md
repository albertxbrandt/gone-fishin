# Gone Fishin'

A text-based fishing game written in Python. The story types out in a Tkinter window, and your choices appear as buttons under it. Every cast, catch, sale, rod purchase, and paid trip is saved to a local SQLite database.

## Play

Run `dist\GoneFishin.exe`. The first time it runs, it creates `fishing.db` next to the exe.

To run from source instead (Python 3.10 or newer, Windows):

```
python main.py
```

## Build the exe

Double-click `create_exe.bat`, or run it from a terminal. It installs PyInstaller from `requirements.txt` and writes `dist\GoneFishin.exe`. Close the game before building, or Windows won't let the old exe be replaced.

## How to play

1. Type a name, or pick a saved player.
2. From the dock, pick a spot. The Pond is free. The Lake, River, and Ocean cost coins and hold rarer fish.
3. Cast your line and wait for the meter to fill, or withdraw the line to cancel the cast.
4. Sell your catch at the Village Shop and buy better rods, which raise the odds of rare fish.

## Project layout

- `main.py` sets up the database and opens the window.
- `gone_fishin/ui` is the frontend (Tkinter only).
- `gone_fishin/logic` holds the game rules and story text (no Tkinter or SQL).
- `gone_fishin/data` holds every SQLite query.
- `docs/PROPOSAL.md` is the project proposal, and `docs/AI_SUMMARY.md` describes how AI was used.

## Database

`location_table`, `item_table`, and `rod_table` list the spots, fish, and rods. The other tables log what the player does and point at those rows by id:

- `player_table`: each angler
- `cast_table`: each cast (player, spot, time, event)
- `event_table`: what the cast produced (fish, junk, or nothing), with event ids starting at 1001
- `inventory_table`: each item caught
- `transaction_table`: coins from sales, and coins spent on rods and travel
