import os
import sys

# Add parent directory to path to import services
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.database_manager import DatabaseManager
from services.auth_manager import AuthManager


def get_db_path() -> str:
    """Get the absolute path to the database file."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(current_dir, "platform.db")
    return db_path


def initialize_database() -> None:
    """Initialize the database with all required tables using DatabaseManager."""
    db_path = get_db_path()
    db = DatabaseManager(db_path)
    db.connect()
    
    try:
        print("🔧 Initializing database tables...")
        
        # Create users table
        db.execute_query("""
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL
            )
        """)
        
        # Create security_incidents table
        db.execute_query("""
            CREATE TABLE IF NOT EXISTS security_incidents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                incident_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                status TEXT NOT NULL,
                description TEXT NOT NULL
            )
        """)
        
        # Create datasets table
        db.execute_query("""
            CREATE TABLE IF NOT EXISTS datasets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                size_bytes INTEGER NOT NULL,
                rows INTEGER NOT NULL,
                source TEXT NOT NULL
            )
        """)
        
        # Create it_tickets table
        db.execute_query("""
            CREATE TABLE IF NOT EXISTS it_tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                priority TEXT NOT NULL,
                status TEXT NOT NULL,
                assigned_to TEXT NOT NULL
            )
        """)
        
        print("✅ Database tables created successfully!")
        
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        raise
    finally:
        db.close()


def seed_sample_data() -> None:
    """Add sample data to the database using OOP pattern."""
    db_path = get_db_path()
    db = DatabaseManager(db_path)
    auth = AuthManager(db)
    
    try:
        print("\n🌱 Seeding sample data...")
        
        # Add sample users using AuthManager
        print("  Adding users...")
        auth.register_user("alice", "password123", "admin")
        auth.register_user("bob", "password456", "analyst")
        auth.register_user("charlie", "password789", "user")
        
        # Add sample security incidents
        print("  Adding security incidents...")
        db.execute_query(
            "INSERT INTO security_incidents (incident_type, severity, status, description) VALUES (?, ?, ?, ?)",
            ("Malware Detection", "critical", "Open", "Ransomware detected on server-03")
        )
        db.execute_query(
            "INSERT INTO security_incidents (incident_type, severity, status, description) VALUES (?, ?, ?, ?)",
            ("SQL Injection", "high", "In Progress", "Attempted SQL injection on login page")
        )
        db.execute_query(
            "INSERT INTO security_incidents (incident_type, severity, status, description) VALUES (?, ?, ?, ?)",
            ("DDoS Attack", "medium", "Resolved", "Brief DDoS attack on main website")
        )
        db.execute_query(
            "INSERT INTO security_incidents (incident_type, severity, status, description) VALUES (?, ?, ?, ?)",
            ("Unauthorized Access", "high", "Open", "Suspicious login attempts from unknown IP")
        )
        
        # Add sample datasets
        print("  Adding datasets...")
        db.execute_query(
            "INSERT INTO datasets (name, size_bytes, rows, source) VALUES (?, ?, ?, ?)",
            ("Customer Analytics", 52428800, 10000, "Internal Database")
        )
        db.execute_query(
            "INSERT INTO datasets (name, size_bytes, rows, source) VALUES (?, ?, ?, ?)",
            ("Sales Data 2024", 104857600, 25000, "Kaggle")
        )
        db.execute_query(
            "INSERT INTO datasets (name, size_bytes, rows, source) VALUES (?, ?, ?, ?)",
            ("User Behavior Logs", 209715200, 50000, "Internal Logs")
        )
        
        # Add sample IT tickets
        print("  Adding IT tickets...")
        db.execute_query(
            "INSERT INTO it_tickets (title, priority, status, assigned_to) VALUES (?, ?, ?, ?)",
            ("VPN connection issues", "high", "Open", "alice")
        )
        db.execute_query(
            "INSERT INTO it_tickets (title, priority, status, assigned_to) VALUES (?, ?, ?, ?)",
            ("Password reset request", "medium", "In Progress", "bob")
        )
        db.execute_query(
            "INSERT INTO it_tickets (title, priority, status, assigned_to) VALUES (?, ?, ?, ?)",
            ("Software installation needed", "low", "Open", "alice")
        )
        db.execute_query(
            "INSERT INTO it_tickets (title, priority, status, assigned_to) VALUES (?, ?, ?, ?)",
            ("Email not working", "critical", "Open", "bob")
        )
        
        print("✅ Sample data added successfully!")
        
    except Exception as e:
        print(f"❌ Error seeding data: {e}")
    finally:
        db.close()


def reset_database() -> None:
    """Reset database by deleting the file and recreating it."""
    db_path = get_db_path()
    
    if os.path.exists(db_path):
        print(f"⚠️  Deleting existing database: {db_path}")
        os.remove(db_path)
    
    print("🔧 Creating fresh database...")
    initialize_database()
    seed_sample_data()
    print("\n✅ Database reset complete!")
    print("\n📝 Test credentials:")
    print("   Username: alice | Password: password123 (admin)")
    print("   Username: bob   | Password: password456 (analyst)")
    print("   Username: charlie | Password: password789 (user)")


if __name__ == "__main__":
    # When run directly, reset the database
    print("=" * 60)
    print("🗄️  DATABASE INITIALIZATION SCRIPT")
    print("=" * 60)
    
    choice = input("\nReset database? This will delete all existing data! (yes/no): ")
    
    if choice.lower() == 'yes':
        reset_database()
    else:
        print("❌ Operation cancelled.")
