"""Database connection and setup.

The whole game shares one SQLite connection. Opening a new connection for every
query is slow, so the connection is created the first time it's needed and
closed once when the game exits.
"""

import sqlite3
from datetime import datetime

from gone_fishin import config
from gone_fishin.data.catalog import seed
from gone_fishin.data.schema import SCHEMA

_connection = None


def connect():
    """Return the shared connection, opening it on first use.

    Use it as `with connect() as conn:`. The `with` block wraps the queries in
    a transaction: it commits if everything succeeds and rolls back on error.
    """
    global _connection
    if _connection is None:
        _connection = sqlite3.connect(config.DB_PATH)
        # SQLite only enforces REFERENCES constraints when this is turned on.
        _connection.execute("PRAGMA foreign_keys = ON")
        # Write-ahead logging: each save appends to a small log file instead of
        # rewriting the database, which makes every cast's save much faster.
        _connection.execute("PRAGMA journal_mode = WAL")
        # With WAL, NORMAL is still crash-safe but waits on the disk less often.
        _connection.execute("PRAGMA synchronous = NORMAL")
    return _connection


def close():
    """Close the shared connection (called when the game exits)."""
    global _connection
    if _connection is not None:
        _connection.close()
        _connection = None


def init_db():
    """Create any missing tables and indexes. Safe to run on every launch."""
    with connect() as conn:
        conn.executescript(SCHEMA)
        seed(conn)


def now():
    """Current time as text with milliseconds, e.g. 2026-11-04 10:16:44.112."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
