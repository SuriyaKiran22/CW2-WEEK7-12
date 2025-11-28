from app.data.db import connect_database

def create_users_table(conn) :
    """Create users table."""
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS users 
                    ( id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT NOT NULL UNIQUE, 
                    password_hash TEXT NOT NULL, role TEXT DEFAULT 'user'
        )
    """)
    conn.commit()
    print("Users table created.")

def create_cyber_incidents_table(conn) :
    """Create cyber_incidents table."""
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS cyber_incidents 
                    ( id INTEGER PRIMARY KEY AUTOINCREMENT,
                      title TEXT,
                      date TEXT,
                      affiliations TEXT,
                      description TEXT,
                      response TEXT,
                      victims TEXT,
                      sponsor TEXT,
                      incident_type TEXT,
                      category TEXT,
                      sources_1 TEXT,
                      sources_2 TEXT,
                      sources_3 TEXT,
                      severity TEXT,
                      status TEXT,
                      reported_by TEXT,
                      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    print("Cyber Incidents table created.")

def create_datasets_metadata_table(conn) :
    """Create datasets_metadata table."""
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS datasets_metadata 
                    ( id INTEGER PRIMARY KEY AUTOINCREMENT, dataset_name TEXT, 
                    file_type TEXT, size_mb REAL, date_created TEXT
        )
    """)
    conn.commit()
    print("Datasets Metadata table created.")

def create_it_tickets_table(conn) :
    """Create it_tickets table."""
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS it_tickets 
                    ( ticket_id TEXT PRIMARY KEY, priority TEXT, status TEXT, 
                    category TEXT, subject TEXT, description TEXT, 
                    created_date TEXT, resolved_date TEXT, assigned_to TEXT
        )
    """)
    conn.commit()
    print("IT Tickets table created.")

def create_all_tables (conn) :
    """Create all tables."""
    create_users_table(conn)
    create_cyber_incidents_table(conn) 
    create_datasets_metadata_table(conn)
    create_it_tickets_table(conn)

if __name__ == "__main__" :
    conn = connect_database()
    create_all_tables(conn)
    conn.close()
    print("\n All tables created successfully.")
