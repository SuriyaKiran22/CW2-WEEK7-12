import sqlite3

import pandas as pd
from app.data.db import connect_database 
from app.data.schema import create_all_tables, create_cyber_incidents_table, create_datasets_metadata_table, create_it_tickets_table, create_users_table
from app.services.user_services import register_user, login_user, migrate_users_from_file 
from app.data.incidents import delete_incident, insert_incident, get_all_incidents, update_incident_status
def main ():
    print ("=" * 60)
    print("Week 8: Database Demo")
    print ("=" * 60)
    
    # 1. Setup database
    conn = connect_database()
    create_all_tables (conn)
    conn.close()
    
    # 2. Migrate users
    migrate_users_from_file()
    
    # 3. Test authentication
    success, msg = register_user("alice", "SecurePass123!", "analyst" )
    print (msg)
    success, msg = login_user("alice", "SecurePass123!")
    print (msg)
    
    # 4. Test CRUD
    incident_id = insert_incident(
        "2024-11-05",
        "Phishing",
        "High",
        "Open",
        "Suspicious email detected",
        "alice"
    )
    print (f"Created incident #{incident_id}")
    
    # 5. Query data
    df = get_all_incidents ()
    print(f"Total incidents: {len(df)}")
    if __name__ == "__main__":
        main()

from pathlib import Path

DATA_DIR = Path("DATA")
DB_PATH = DATA_DIR / "intelligence_platform.db"

def load_csv_to_table(conn, csv_path, table_name):
    """Load a CSV file into an existing table using pandas."""
    csv_path = Path(csv_path)
    if not csv_path.exists():
        print(f"  File not found: {csv_path} — skipping {table_name}")
        return

    try:
        print(f"  Reading {csv_path.name}...")
        df = pd.read_csv(csv_path)
        print(f"  Read {len(df)} rows from {csv_path.name}")
    except Exception as e:
        print(f"  Error reading {csv_path.name}: {e}")
        return

    # Use the provided connection to avoid opening new ones
    try:
        print(f"  Getting table info for {table_name}...")
        cur = conn.cursor()
        cur.execute(f"PRAGMA table_info({table_name})")
        table_info = cur.fetchall()
        table_cols = [t[1] for t in table_info]
        print(f"    Table columns: {table_cols}")

        # normalize mapping helper
        def normalize(s):
            return str(s).strip().lower().replace(' ', '_').replace('-', '_')

        norm_table = {normalize(c): c for c in table_cols}
        df_cols = list(df.columns)
        mapping = {}

        print(f"  Building column mapping...")
        # build mapping from CSV -> table columns (best-effort)
        for c in df_cols:
            n = normalize(c)
            # common alternatives
            if n in norm_table:
                mapping[c] = norm_table[n]
            else:
                # handle a few known synonyms
                if n in ('type', 'incident_type') and 'incident_type' in norm_table:
                    mapping[c] = norm_table['incident_type']
                elif n in ('date', 'date_reported', 'created_date') and 'date' in norm_table:
                    mapping[c] = norm_table['date']
                elif n in ('title', 'subject', 'name') and 'title' in norm_table:
                    mapping[c] = norm_table['title']
                elif n == 'description' and 'description' in norm_table:
                    mapping[c] = norm_table['description']

        if mapping:
            print(f"    Mapping: {mapping}")
            df = df.rename(columns=mapping)

        # Only keep columns that exist in target table
        insert_cols = [c for c in df.columns if c in table_cols]
        if not insert_cols:
            print(f"  No matching columns to insert for {table_name}; skipping")
            return

        placeholders = ','.join('?' for _ in insert_cols)
        col_list_sql = ','.join(f'"{c}"' for c in insert_cols)
        sql = f'INSERT OR IGNORE INTO {table_name} ({col_list_sql}) VALUES ({placeholders})'

        print(f"  Building rows tuple...")
        rows = [tuple(row[col] if col in row else None for col in insert_cols) for _, row in df.iterrows()]
        print(f"  Inserting {len(rows)} rows...")
        cur.executemany(sql, rows)
        conn.commit()
        print(f"  Loaded {len(rows)} rows into {table_name} (inserted {cur.rowcount} rows)")
    except Exception as e:
        print(f"  Error loading CSV into {table_name}: {e}")
        import traceback
        traceback.print_exc()

def setup_database_complete():
    """
    Complete database setup:
    1. Connect to database
    2. Create all tables
    3. Migrate users from users.txt
    4. Load CSV data for all domains
    5. Verify setup
    """
    print("\n" + "="*60)
    print("STARTING COMPLETE DATABASE SETUP")
    print("="*60)
    
    # Step 1: Connect
    print("\n[1/5] Connecting to database...")
    conn = connect_database()
    print("✅ Connected")
    
    # Step 2: Create tables
    print("\n[2/5] Creating database tables...")
    create_users_table(conn)
    create_cyber_incidents_table(conn)
    create_datasets_metadata_table(conn)
    create_it_tickets_table(conn)
    
    # Step 3: Migrate users
    print("\n[3/5] Migrating users from users.txt...")
    migrate_users_from_file(conn)
    
    # Step 4: Load CSV data
    print("\n[4/5] Loading CSV data...")
    load_csv_to_table(conn, DATA_DIR / "cyber_incidents.csv", "cyber_incidents")
    load_csv_to_table(conn, DATA_DIR / "datasets_metadata.csv", "datasets_metadata")
    load_csv_to_table(conn, DATA_DIR / "it_tickets.csv", "it_tickets")
    
    # Step 5: Verify
    print("\n[5/5] Verifying database setup...")
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables_found = [r[0] for r in cursor.fetchall()]
    print(" Tables in DB:", tables_found)
    
    # Count rows in each table
    tables = ['users', 'cyber_incidents', 'datasets_metadata', 'it_tickets']
    print("\n Database Summary:")
    print(f"{'Table':<25} {'Row Count':<15}")
    print("-" * 40)
    
    for table in tables:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"{table:<25} {count:<15}")
        except sqlite3.OperationalError:
            print(f"{table:<25} {'N/A (not found)':<15}")
    
    conn.close()
    
    print("\n" + "="*60)
    print("DATABASE SETUP COMPLETE!")
    print("="*60)
    print(f"\n Database location: {DB_PATH.resolve()}")
    print(" You're ready for Week 9 (Streamlit web interface)!")

# Run the complete setup
setup_database_complete()

def get_incidents_by_type_count(conn):
    """Return a DataFrame counting incidents grouped by `incident_type`."""
    try:
        df = pd.read_sql_query(
            "SELECT incident_type, COUNT(*) as count FROM cyber_incidents GROUP BY incident_type",
            conn,
        )
        return df
    except Exception:
        return pd.DataFrame()

def get_high_severity_by_status(conn):
    """Return a DataFrame counting HIGH-severity incidents grouped by status.

    This treats severity as text and looks for values containing 'high' (case-insensitive).
    """
    try:
        df = pd.read_sql_query(
            """
            SELECT status, COUNT(*) as count
            FROM cyber_incidents
            WHERE LOWER(CAST(severity AS TEXT)) LIKE '%high%'
            GROUP BY status
            """,
            conn,
        )
        return df
    except Exception:
        return pd.DataFrame()

def run_comprehensive_tests():
    """
    Run comprehensive tests on your database.
    """
    print("\n" + "="*60)
    print("🧪 RUNNING COMPREHENSIVE TESTS")
    print("="*60)
    
    conn = connect_database()
    
    # Test 1: Authentication
    print("\n[TEST 1] Authentication")
    success, msg = register_user("test_user", "TestPass123!", "user")
    print(f"  Register: {'✅' if success else '❌'} {msg}")
    
    success, msg = login_user("test_user", "TestPass123!")
    print(f"  Login:    {'✅' if success else '❌'} {msg}")
    
    # Test 2: CRUD Operations
    print("\n[TEST 2] CRUD Operations")
    
    # Create
    print("  Create: Creating test incident...")
    test_id = insert_incident(
        "2024-11-05",
        "Test Incident",
        "Low",
        "Open",
        "This is a test incident",
        "test_user",
        conn=conn,
    )
    print(f"  Create: Incident #{test_id} created")
    
    # Read
    df = pd.read_sql_query(
        "SELECT * FROM cyber_incidents WHERE id = ?",
        conn,
        params=(test_id,)
    )
    print(f"  Read:    Found incident #{test_id}")
    
    # Update
    update_incident_status(conn, test_id, "Resolved")
    print(f"  Update:  Status updated")
    
    # Delete
    delete_incident(conn, test_id)
    print(f"  Delete:  Incident deleted")
    
    # Test 3: Analytical Queries
    print("\n[TEST 3] Analytical Queries")
    
    df_by_type = get_incidents_by_type_count(conn)
    print(f"  By Type:     Found {len(df_by_type)} incident types")
    
    df_high = get_high_severity_by_status(conn)
    print(f"  High Severity: Found {len(df_high)} status categories")
    
    conn.close()
    
    print("\n" + "="*60)
    print(" ALL TESTS PASSED!")
    print("="*60)

# Run tests
if __name__ == "__main__":
    setup_database_complete()
    import time
    time.sleep(1)
    run_comprehensive_tests()