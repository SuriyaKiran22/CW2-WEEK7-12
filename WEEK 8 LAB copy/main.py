from app.data.db import connect_database
from app.data.schema import create_all_tables
from app.services.user_service import register_user, login_user, migrate_users_from_file
from app.data.incidents import insert_incident, get_all_incidents
from app.data.tickets import insert_ticket, get_all_tickets
from app.data.datasets import insert_dataset, get_all_datasets
from app.data.users import insert_user, get_all_users
import pandas as pd


def load_csv_data():
    """Load CSV data into the database"""
    try:
        users_df = pd.read_csv('DATA/users.csv')
        users_df.to_sql('users', connect_database(), if_exists='replace', index=False)
        print(f" Loaded {len(users_df)} users")
    except Exception as e:
        print(f"  Users: {e}")
    
    try:
        incidents_df = pd.read_csv('DATA/cyber_incidents.csv')
        incidents_df.to_sql('cyber_incidents', connect_database(), if_exists='replace', index=False)
        print(f" Loaded {len(incidents_df)} cyber incidents")
    except Exception as e:
        print(f"  Incidents: {e}")
    
    try:
        tickets_df = pd.read_csv('DATA/it_tickets.csv')
        tickets_df.to_sql('it_tickets', connect_database(), if_exists='replace', index=False)
        print(f" Loaded {len(tickets_df)} IT tickets")
    except Exception as e:
        print(f"  Tickets: {e}")
    
    try:
        datasets_df = pd.read_csv('DATA/datasets_metadata.csv')
        datasets_df.to_sql('datasets_metadata', connect_database(), if_exists='replace', index=False)
        print(f" Loaded {len(datasets_df)} datasets")
    except Exception as e:
        print(f"  Datasets: {e}")


def test_authentication():
    """Test user registration and login"""
    success, msg = register_user("bob", "SecurePass123!", "analyst")
    print(f"Register: {msg}")
    
    success, msg = login_user("bob", "SecurePass123!")
    print(f"Login: {msg}")


def test_crud():
    """Test CRUD operations"""
    # Test incidents
    incident_id = insert_incident(
        date="2024-11-05",
        incident_type="Phishing",
        severity="High",
        status="Open",
        description="Suspicious email detected",
        reported_by="bob"
    )
    print(f"Created incident #{incident_id}")
    df = get_all_incidents()
    print(f"Total incidents after insertion: {len(df)}")
    
    # Test tickets
    ticket_id = insert_ticket(
        id=None,
        title="Cannot access VPN",
        priority="High",
        status="Open",
        created_date="2024-11-05"
    )   
    print(f"Created ticket #{ticket_id}")
    df_tickets = get_all_tickets()
    print(f"Total tickets after insertion: {len(df_tickets)}")
    
    # Test datasets
    dataset_id = insert_dataset(
        id=None,
        name="Employee Data",
        source="HR System",
        category="Internal",
        size=2048
    )
    print(f"Created dataset #{dataset_id}")
    df_datasets = get_all_datasets()
    print(f"Total datasets after insertion: {len(df_datasets)}")
    
    # Test users
    insert_user(
        id=None,
        username="alice",
        password_hash="hashed_password_123",
        role="admin"
    )
    users = get_all_users()
    print(f"Total users after insertion: {len(users)}")
    print("\nFirst 5 users:")
    print(pd.DataFrame(users).head(5))
    

 


def query_data():
    """Query and display all data"""
    # Query incidents
    df_incidents = get_all_incidents()
    print(f"Total incidents: {len(df_incidents)}")
    print("\nFirst 5 incidents:")
    print(df_incidents.head(5))
    
    # Query tickets
    df_tickets = get_all_tickets()
    print(f"\nTotal tickets: {len(df_tickets)}")
    print("\nFirst 5 tickets:")
    print(df_tickets.head(5))
    
    # Query datasets
    df_datasets = get_all_datasets()
    print(f"\nTotal datasets: {len(df_datasets)}")
    print("\nFirst 5 datasets:")
    print(df_datasets.head(5))
    
    # Query users
    users = get_all_users()
    df_users = pd.DataFrame(users)
    print(f"\nTotal users: {len(users)}")
    print("\nFirst 5 users:")
    print(df_users.head(5))



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
