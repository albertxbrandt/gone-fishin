"""SQL that creates the game's tables.

The first three tables name the things the game is about (spots, fish, rods).
The rest record what the player does, and they point at those rows by id
instead of storing the name a second time.

Every statement uses IF NOT EXISTS, so running it again only adds what is missing.
"""

SCHEMA = """
-- The fishing spots. cast_table.location and travel fees point here.
CREATE TABLE IF NOT EXISTS location_table (
    location_id   INTEGER PRIMARY KEY,
    location_name TEXT NOT NULL,
    travel_fee    INTEGER NOT NULL
);

-- Every fish and piece of junk. Catches, inventory, and sales point here.
CREATE TABLE IF NOT EXISTS item_table (
    item_id   INTEGER PRIMARY KEY,
    item_name TEXT NOT NULL,
    rarity    INTEGER NOT NULL,
    value     INTEGER NOT NULL
);

-- The fishing rods the shop sells. Purchases point here.
CREATE TABLE IF NOT EXISTS rod_table (
    rod_id   INTEGER PRIMARY KEY,
    rod_name TEXT NOT NULL,
    price    INTEGER NOT NULL,
    luck     REAL NOT NULL
);

-- One row per angler.
CREATE TABLE IF NOT EXISTS player_table (
    player_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    player_name TEXT NOT NULL UNIQUE,
    created_at  TEXT NOT NULL
);

-- What happened on a cast. event_type: 1 = fish, 2 = junk, 3 = nothing.
-- item_id is empty when nothing was caught.
CREATE TABLE IF NOT EXISTS event_table (
    event_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type INTEGER NOT NULL,
    item_id    INTEGER REFERENCES item_table(item_id),
    weight_lb  REAL
);

-- One row per cast: who cast, where, when, and which event it produced.
CREATE TABLE IF NOT EXISTS cast_table (
    cast_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    player_id INTEGER NOT NULL REFERENCES player_table(player_id),
    location  INTEGER NOT NULL REFERENCES location_table(location_id),
    timestamp TEXT NOT NULL,
    event_id  INTEGER NOT NULL REFERENCES event_table(event_id)
);

-- One row per item caught. Rows are never deleted, even after the item is sold.
CREATE TABLE IF NOT EXISTS inventory_table (
    inventory_id INTEGER PRIMARY KEY AUTOINCREMENT,
    player_id    INTEGER NOT NULL REFERENCES player_table(player_id),
    event_id     INTEGER NOT NULL REFERENCES event_table(event_id),
    item_id      INTEGER NOT NULL REFERENCES item_table(item_id),
    obtained_at  TEXT NOT NULL
);

-- Every coin movement. A player's balance is the SUM of their coins column.
-- kind: 1 = sale (item_id and inventory_id set), 2 = rod purchase (rod_id set),
--       3 = travel fee (location_id set). Sales are positive, spending is negative.
CREATE TABLE IF NOT EXISTS transaction_table (
    transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    player_id      INTEGER NOT NULL REFERENCES player_table(player_id),
    kind           INTEGER NOT NULL,
    item_id        INTEGER REFERENCES item_table(item_id),
    rod_id         INTEGER REFERENCES rod_table(rod_id),
    location_id    INTEGER REFERENCES location_table(location_id),
    coins          INTEGER NOT NULL,
    inventory_id   INTEGER REFERENCES inventory_table(inventory_id),
    timestamp      TEXT NOT NULL
);

-- Indexes let SQLite jump straight to one player's rows instead of scanning
-- every row, which keeps the game fast as the save file grows.
CREATE INDEX IF NOT EXISTS idx_cast_player ON cast_table(player_id);
CREATE INDEX IF NOT EXISTS idx_inventory_player ON inventory_table(player_id);
CREATE INDEX IF NOT EXISTS idx_transaction_player ON transaction_table(player_id, kind);
-- Used to find which inventory items have already been sold.
CREATE INDEX IF NOT EXISTS idx_transaction_inventory ON transaction_table(inventory_id);

-- Start event ids at 1001 to match the assignment example.
INSERT INTO sqlite_sequence (name, seq)
SELECT 'event_table', 1000
WHERE NOT EXISTS (SELECT 1 FROM sqlite_sequence WHERE name = 'event_table');
"""
