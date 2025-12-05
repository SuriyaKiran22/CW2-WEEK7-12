import sqlite3
from pathlib import Path

# The path is relative to the directory where the script is executed.
DB_PATH = Path("DATA") / "intelligence_platform.db" 

def connect_database(db_path=DB_PATH):
    """
    Connect to SQLite database. Creates file and parent directory if they don't exist.
    """
    try:
        # Ensure the parent directory (DATA/) exists before connecting.
        db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Connect to the database
        return sqlite3.connect(str(db_path))
    except Exception as e:
        print(f"Failed to connect to database at path: {Path(db_path).resolve()}")
        raise e

def close_database(conn):
    """Close the database connection safely."""
    if conn:
        conn.close()