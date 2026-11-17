"""Copies the game's spots, fish, and rods into their lookup tables.

The catalogs in the logic package stay the place where gameplay is edited.
This copies the id, name, and the numbers the other tables rely on, so a saved
game explains itself: location 1 joins to "Lake" instead of being a bare number.
"""

from gone_fishin.logic.locations import LOCATIONS
from gone_fishin.logic.rods import RODS


def seed(conn):
    """Insert or update every spot, item, and rod. Safe to run on every launch."""
    conn.executemany(
        "INSERT INTO location_table (location_id, location_name, travel_fee) VALUES (?, ?, ?) "
        "ON CONFLICT(location_id) DO UPDATE SET "
        "location_name = excluded.location_name, travel_fee = excluded.travel_fee",
        [(loc.location_id, loc.name, loc.travel_fee) for loc in LOCATIONS.values()],
    )
    items = {
        catch.item_id: (catch.item_id, catch.item_name, catch.rarity, catch.value)
        for loc in LOCATIONS.values()
        for catch in loc.catches
        if catch.item_id
    }
    conn.executemany(
        "INSERT INTO item_table (item_id, item_name, rarity, value) VALUES (?, ?, ?, ?) "
        "ON CONFLICT(item_id) DO UPDATE SET "
        "item_name = excluded.item_name, rarity = excluded.rarity, value = excluded.value",
        list(items.values()),
    )
    conn.executemany(
        "INSERT INTO rod_table (rod_id, rod_name, price, luck) VALUES (?, ?, ?, ?) "
        "ON CONFLICT(rod_id) DO UPDATE SET "
        "rod_name = excluded.rod_name, price = excluded.price, luck = excluded.luck",
        [(rod.rod_id, rod.name, rod.price, rod.luck) for rod in RODS],
    )
