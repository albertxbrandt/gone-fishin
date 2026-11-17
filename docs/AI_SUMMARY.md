# How I used AI

I built Gone Fishin' in Cursor with an AI coding assistant. I took the whole idea of a text-based game from the example provided but still wanted to design my own game. I chose a fishing game because I played a fishing game on steam recently and it inspired me to make a text based one. I had the assistant write the Python, split it into files, and rebuilt the `.exe`. I checked the window and the database after each change and sent it back when something was wrong.

## What I used it for

- Turning the assignment into a small fishing game.
- A text window: story text that types out, a blinking cursor, and choice buttons under the prompt.
- Saving every cast, catch, sale, and trip in SQLite, with separate files for the window, the game rules, and the database.
- Coins, fish rarities, a shop, and rods that change the odds of rare fish.
- A free pond, paid trips to the other spots, a confirmation before traveling, and an "ask about this rod" page before buying.
- A random 3 to 20 second wait while a cast is out, with a Withdraw Line button.
- Lookup tables for spots, fish, and rods, so the log tables store ids and the names live in one place.

## Difficulties

- The first build was a regular window with panels. I changed it to a text game, and the buttons had to stay under the story without stacking into a third row.
- One early version of Withdraw Line cancelled the wait but never showed the next screen. A cast also had to be saved only if the player waited for the bite.
- The Lake was stored as the number `1` in the cast log and as the word `"Lake"` on a travel fee. Lookup tables fixed that, but the old `fishing.db` could not be reused.
- Saving a cast was slow at first because the game opened a new database connection every time. Reusing one connection and turning on write-ahead logging made a few hundred casts take a fraction of a second.
