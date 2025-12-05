import sqlite3

def create_users_table(conn):
    """Create the users table."""
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL
        )
    """)
    print(" Users table created")

def create_incidents_table(conn):
    """Create the cyber_incidents table."""
    cursor = conn.cursor()
    # FIX: Added 'incident_type' column, which was missing.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cyber_incidents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            incident_type TEXT NOT NULL, 
            severity TEXT NOT NULL,
            status TEXT NOT NULL,
            description TEXT,
            reported_by TEXT
        )
    """)
    print(" Cyber incidents table created")

def create_datasets_metadata_table(conn):
    """Create the datasets_metadata table."""
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS datasets_metadata (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            description TEXT,
            created_at TEXT
        )
    """)
    print(" Datasets metadata table created")

def create_it_tickets_table(conn):
    """Create the IT tickets table."""
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS it_tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            priority TEXT NOT NULL,
            status TEXT NOT NULL,
            summary TEXT
        )
    """)
    print(" IT tickets table created")

def create_all_tables(conn):
    """Creates all necessary tables in the database."""
    create_users_table(conn)
    create_incidents_table(conn)
    create_datasets_metadata_table(conn)
    create_it_tickets_table(conn)
    conn.commit()