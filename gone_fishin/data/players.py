"""Queries for player_table."""

from gone_fishin.data.database import connect, now


def list_names():
    """Names of every saved player, oldest first (used by the "Have we met?" screen)."""
    with connect() as conn:
        rows = conn.execute("SELECT player_name FROM player_table ORDER BY player_id").fetchall()
    return [row[0] for row in rows]


def get_or_create(name):
    """Load the player with this name, or create them. Returns (player_id, is_new)."""
    with connect() as conn:
        row = conn.execute(
            "SELECT player_id FROM player_table WHERE player_name = ?", (name,)
        ).fetchone()
        if row:
            return row[0], False
        cur = conn.execute(
            "INSERT INTO player_table (player_name, created_at) VALUES (?, ?)",
            (name, now()),
        )
        return cur.lastrowid, True
