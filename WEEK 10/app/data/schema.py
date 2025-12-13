from app.data.db import connect_database


def create_users_table(conn):
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'user'
        )
    """)
    conn.commit()
    print("✓ Users table created")


def create_cyber_incidents_table(conn):
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cyber_incidents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            incident_type TEXT,
            severity TEXT,
            status TEXT,
            description TEXT,
            reported_by TEXT
        )
    """)
    conn.commit()
    print(" Cyber incidents table created")


def create_datasets_metadata_table(conn):
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS datasets_metadata (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT,
            source TEXT,
            size INTEGER          
        )
    """)
    conn.commit()
    print(" Datasets metadata table created")


def create_it_tickets_table(conn):
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS it_tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            priority TEXT,
            status TEXT,
            created_date TEXT
        )
    """)
    conn.commit()
    print(" IT tickets table created")


def create_all_tables(conn):
    create_users_table(conn)
    create_cyber_incidents_table(conn)
    create_datasets_metadata_table(conn)
    create_it_tickets_table(conn)


if __name__ == "__main__":
    conn = connect_database()
    create_all_tables(conn)
    conn.close()
    print("\n All tables created!")
