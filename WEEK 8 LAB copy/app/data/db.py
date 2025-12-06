"""Database Connection Module"""

import sqlite3
from pathlib import Path

DB_PATH = Path("DATA") / "intelligence_platform.db"


def connect_database(db_path=DB_PATH):
    """Connect to SQLite database. Creates file if it doesn't exist."""
    return sqlite3.connect(str(db_path))



def close_database(conn):
    """Close the database connection safely."""
    if conn:
        conn.close()


if __name__ == "__main__":
    try:
        conn = connect_database()
        print(f" Connected to database: {DB_PATH}")
        close_database(conn)
    except Exception as e:
        print(f" Error: {e}")
