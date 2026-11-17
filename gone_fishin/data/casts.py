"""Queries for cast_table, the log of every line the player casts."""

from gone_fishin.data import events, inventory
from gone_fishin.data.database import connect, now


def record_cast(player_id, location_id, outcome):
    """Log one cast.

    Writes the event, the cast that caused it, and (if something was caught) the
    inventory item. All three happen in one transaction, so a crash can't leave
    a cast without its event.
    """
    timestamp = now()
    with connect() as conn:
        event_id = events.add_event(conn, outcome)
        conn.execute(
            "INSERT INTO cast_table (player_id, location, timestamp, event_id) VALUES (?, ?, ?, ?)",
            (player_id, location_id, timestamp, event_id),
        )
        if outcome.item_id:
            inventory.add_item(conn, player_id, event_id, outcome.item_id, timestamp)


def recent_casts(player_id, limit):
    """The player's latest casts, newest first, as [(timestamp, location_id, event_type, item_name)]."""
    with connect() as conn:
        return conn.execute(
            "SELECT c.timestamp, c.location, e.event_type, it.item_name "
            "FROM cast_table c JOIN event_table e ON e.event_id = c.event_id "
            "LEFT JOIN item_table it ON it.item_id = e.item_id "
            "WHERE c.player_id = ? ORDER BY c.cast_id DESC LIMIT ?",
            (player_id, limit),
        ).fetchall()
