"""Queries for inventory_table."""

from gone_fishin.data.database import connect


def add_item(conn, player_id, event_id, item_id, obtained_at):
    """Put a caught item in the player's bag (runs inside the caller's transaction)."""
    conn.execute(
        "INSERT INTO inventory_table (player_id, event_id, item_id, obtained_at) "
        "VALUES (?, ?, ?, ?)",
        (player_id, event_id, item_id, obtained_at),
    )


def list_unsold(player_id):
    """Items still in the bag, newest first.

    Each row is (inventory_id, item_id, item_name, rarity, value).
    An item counts as sold once a sale points at it, so the LEFT JOIN keeps only
    items with no matching sale. The name, rarity, and value come from item_table.
    """
    with connect() as conn:
        return conn.execute(
            "SELECT i.inventory_id, i.item_id, it.item_name, it.rarity, it.value "
            "FROM inventory_table i "
            "JOIN item_table it ON it.item_id = i.item_id "
            "LEFT JOIN transaction_table t ON t.inventory_id = i.inventory_id "
            "WHERE i.player_id = ? AND t.transaction_id IS NULL "
            "ORDER BY i.inventory_id DESC",
            (player_id,),
        ).fetchall()
