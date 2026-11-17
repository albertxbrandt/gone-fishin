"""Queries for event_table."""


def add_event(conn, outcome):
    """Save what a cast produced and return its new event_id.

    Takes an open connection so it runs inside the caller's transaction
    (see casts.record_cast).
    """
    cur = conn.execute(
        "INSERT INTO event_table (event_type, item_id, weight_lb) VALUES (?, ?, ?)",
        (outcome.event_type, outcome.item_id, outcome.weight_lb),
    )
    return cur.lastrowid
