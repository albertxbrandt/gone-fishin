"""The fishing spots and everything that can be caught at each one."""

from dataclasses import dataclass

# Values stored in event_table.event_type
FISH, JUNK, NOTHING = 1, 2, 3
EVENT_TYPES = {FISH: "Fish", JUNK: "Junk", NOTHING: "Nothing"}

# Rarity tiers. Better rods multiply a catch's chance once per tier (see fishing.py).
COMMON, UNCOMMON, RARE, LEGENDARY = 0, 1, 2, 3
RARITY_NAMES = {COMMON: "Common", UNCOMMON: "Uncommon", RARE: "Rare", LEGENDARY: "Legendary"}


@dataclass(frozen=True)
class Catch:
    """One possible result of a cast."""
    event_type: int
    item_name: str | None  # None means nothing was caught
    min_lb: float          # weight range, picked at random on each catch
    max_lb: float
    chance: int            # relative odds: a catch with chance 30 is 3x as likely as one with 10
    rarity: int = COMMON
    value: int = 0         # coins the shop pays
    item_id: int | None = None  # row in item_table; None for a catch of nothing


@dataclass(frozen=True)
class Location:
    location_id: int  # stored in cast_table.location
    name: str
    travel_fee: int   # coins charged each trip; 0 means free
    arrival_text: str
    catches: tuple


# Ids are stored in cast_table, so existing spots keep their original ids; dict order is the dock button order.
LOCATIONS = {
    4: Location(4, "Pond", 0, "You wander over to the village pond. Ducks paddle past the reeds.", (
        Catch(FISH, "Minnow", 0.1, 0.3, 40, COMMON, 1, 1),
        Catch(FISH, "Bluegill", 0.3, 1.0, 30, COMMON, 2, 2),
        Catch(FISH, "Carp", 2.0, 8.0, 15, COMMON, 3, 3),
        Catch(JUNK, "Old Boot", 1.0, 2.0, 10, COMMON, 1, 4),
        Catch(NOTHING, None, 0, 0, 15),
    )),
    1: Location(1, "Lake", 10, "You walk down to the lake. The water is glassy and calm.", (
        Catch(FISH, "Trout", 1.0, 5.0, 35, COMMON, 5, 5),
        Catch(FISH, "Bass", 1.5, 8.0, 25, UNCOMMON, 10, 6),
        Catch(FISH, "Catfish", 3.0, 20.0, 8, RARE, 25, 7),
        Catch(FISH, "Golden Koi", 2.0, 6.0, 1, LEGENDARY, 150, 8),
        Catch(JUNK, "Tin Can", 0.2, 0.5, 10, COMMON, 1, 9),
        Catch(NOTHING, None, 0, 0, 20),
    )),
    2: Location(2, "River", 30, "You hike to the river. The current rushes over smooth rocks.", (
        Catch(FISH, "Rainbow Trout", 2.0, 8.0, 30, UNCOMMON, 15, 10),
        Catch(FISH, "Salmon", 4.0, 15.0, 25, UNCOMMON, 12, 11),
        Catch(FISH, "Pike", 3.0, 18.0, 15, RARE, 30, 12),
        Catch(FISH, "Sturgeon", 40.0, 150.0, 2, LEGENDARY, 180, 13),
        Catch(JUNK, "Rusty Hook", 0.1, 0.2, 10, COMMON, 1, 14),
        Catch(NOTHING, None, 0, 0, 25),
    )),
    3: Location(3, "Ocean", 80, "You row out past the breakers. Salt spray hits your face.", (
        Catch(FISH, "Mackerel", 1.0, 4.0, 25, UNCOMMON, 12, 15),
        Catch(FISH, "Tuna", 10.0, 60.0, 25, RARE, 40, 16),
        Catch(FISH, "Swordfish", 50.0, 200.0, 12, RARE, 60, 17),
        Catch(FISH, "Giant Squid", 100.0, 400.0, 3, LEGENDARY, 300, 18),
        Catch(JUNK, "Seaweed", 0.5, 3.0, 15, COMMON, 1, 19),
        Catch(NOTHING, None, 0, 0, 25),
    )),
}

