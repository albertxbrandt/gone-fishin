"""Queries for transaction_table: coins earned from sales and spent on rods and travel."""

from gone_fishin.data.database import connect, now

# Values stored in transaction_table.kind
SALE, PURCHASE, TRAVEL = 1, 2, 3


def balance(player_id):
    """The player's coins: earnings are positive rows and spending is negative, so it's just the sum."""
    with connect() as conn:
        row = conn.execute(
            "SELECT COALESCE(SUM(coins), 0) FROM transaction_table WHERE player_id = ?", (player_id,)
        ).fetchone()
    return row[0]


def sell_items(player_id, sales):
    """Record a sale for each item. sales is [(inventory_id, item_id, coins)]. Returns total coins earned."""
    timestamp = now()
    with connect() as conn:
        # executemany inserts every row in a single call, which is faster than one call per item.
        conn.executemany(
            "INSERT INTO transaction_table (player_id, kind, item_id, coins, inventory_id, timestamp) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            [(player_id, SALE, item_id, coins, inventory_id, timestamp) for inventory_id, item_id, coins in sales],
        )
    return sum(coins for _, _, coins in sales)


def buy_rod(player_id, rod_id, price):
    """Record a rod purchase. The cost is stored as a negative amount."""
    with connect() as conn:
        conn.execute(
            "INSERT INTO transaction_table (player_id, kind, rod_id, coins, timestamp) VALUES (?, ?, ?, ?, ?)",
            (player_id, PURCHASE, rod_id, -price, now()),
        )


def pay_travel(player_id, location_id, price):
    """Record a travel fee. The cost is stored as a negative amount."""
    with connect() as conn:
        conn.execute(
            "INSERT INTO transaction_table (player_id, kind, location_id, coins, timestamp) VALUES (?, ?, ?, ?, ?)",
            (player_id, TRAVEL, location_id, -price, now()),
        )


def purchased_rod_ids(player_id):
    """Ids of the rods the player has bought (the free starter rod is not in here)."""
    with connect() as conn:
        rows = conn.execute(
            "SELECT rod_id FROM transaction_table WHERE player_id = ? AND kind = ?", (player_id, PURCHASE)
        ).fetchall()
    return {row[0] for row in rows}
