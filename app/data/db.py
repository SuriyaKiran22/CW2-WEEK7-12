import sqlite3
from pathlib import Path

# Path to the SQLite database file (use consistent .db filename)
DB_PATH = Path("DATA") / "intelligence_platform.db"

def connect_database(db_path=DB_PATH):
    """Connect to SQLite database, ensuring the DATA directory exists.

    Use a slightly longer timeout to tolerate transient locks during bulk imports.
    """
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(str(db_path), timeout=10, check_same_thread=False)


def create_tables(conn=None):
    """No-op placeholder. Table creation is handled in app/data/schema.py.

    Kept for backward compatibility if other modules call it.
    """
    return
