from app.data.db import connect_database
from app.data.schema import create_all_tables
from app.services.user_service import register_user, login_user, migrate_users_from_file
from app.data.incidents import insert_incident, get_all_incidents
import pandas as pd
from pathlib import Path
import os

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "DATA"


def load_csv_data():
    print(" Verifying data file paths...")
    
    try:
        users_file_path = DATA_DIR / 'users.csv'
        users_df = pd.read_csv(users_file_path)
        users_df.to_sql('users', connect_database(), if_exists='replace', index=False)
        print(f" Loaded {len(users_df)} users")
    except FileNotFoundError:
        print(f"Users: [Errno 2] No such file or directory: '{users_file_path}' (Verify file exists in {DATA_DIR})")
    except Exception as e:
        print(f"Users: Error: {e}")
    
    try:
        incidents_file_path = DATA_DIR / 'cyber_incidents.csv'
        incidents_df = pd.read_csv(incidents_file_path)
        incidents_df.to_sql('cyber_incidents', connect_database(), if_exists='replace', index=False)
        print(f" Loaded {len(incidents_df)} cyber incidents")
    except FileNotFoundError:
        print(f"Incidents: [Errno 2] No such file or directory: '{incidents_file_path}' (Verify file exists in {DATA_DIR})")
    except Exception as e:
        print(f"Incidents: Error: {e}")
    
    try:
        tickets_file_path = DATA_DIR / 'it_tickets.csv'
        tickets_df = pd.read_csv(tickets_file_path)
        tickets_df.to_sql('it_tickets', connect_database(), if_exists='replace', index=False)
        print(f" Loaded {len(tickets_df)} IT tickets")
    except FileNotFoundError:
        print(f"Tickets: [Errno 2] No such file or directory: '{tickets_file_path}' (Verify file exists in {DATA_DIR})")
    except Exception as e:
        print(f"Tickets: Error: {e}")
    
    try:
        datasets_file_path = DATA_DIR / 'datasets_metadata.csv'
        datasets_df = pd.read_csv(datasets_file_path)
        datasets_df.to_sql('datasets_metadata', connect_database(), if_exists='replace', index=False)
        print(f" Loaded {len(datasets_df)} datasets")
    except FileNotFoundError:
        print(f"Datasets: [Errno 2] No such file or directory: '{datasets_file_path}' (Verify file exists in {DATA_DIR})")
    except Exception as e:
        print(f"Datasets: Error: {e}")


def test_authentication():
    success, msg = register_user("bob", "SecurePass123!", "analyst")
    print(f"Register: {msg}")
    
    success, msg = login_user("bob", "SecurePass123!")
    print(f"Login: {msg}")


def test_crud():
    incident_id = insert_incident(
        date="2024-11-05",
        incident_type="Phishing",
        severity="High",
        status="Open",
        description="Suspicious email detected",
        reported_by="bob"
    )
    print(f"Created incident #{incident_id}")


def query_data():
    df = get_all_incidents()
    print(f"Total incidents: {len(df)}")
    print("\nFirst 5 incidents:")
    print(df.head(5))


def main():
    print("=" * 60)
    print("Week 8: Database Demo")
    print("=" * 60)
    
    print("\n[1/6] Setting up database...")
    conn = connect_database()
    create_all_tables(conn)
    conn.close()
    
    print("\n[2/6] Loading CSV data...")
    load_csv_data()
    
    print("\n[3/6] Testing authentication...")
    test_authentication()
    
    print("\n[4/6] Testing CRUD operations...")
    test_crud()
    
    print("\n[5/6] Querying data...")
    query_data()
    
    print("\n" + "=" * 60)
    print(" Demo Complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()