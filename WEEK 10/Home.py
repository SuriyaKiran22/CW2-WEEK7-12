import streamlit as st
import pandas as pd
import sys
import os 

from app.data.schema import create_users_table
from app.data.db import connect_database
from pathlib import Path

# Initialize database with users table only (not from CSV for login)
conn = None
try:
    conn = connect_database()
    cursor = conn.cursor()
    
    # Create users table with proper structure for login
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'user'
        )
    """)
    conn.commit()
except Exception as e:
    st.exception(f"FATAL: Database initialization failed during table creation.")
    st.stop()
finally:
    if conn:
        conn.close()


current_dir = os.path.dirname(__file__)
project_root = os.path.join(current_dir)
if project_root not in sys.path:
    sys.path.append(project_root)

from app.services.user_service import login_user, register_user


st.set_page_config(
    page_title="Intelligence Platform",
    page_icon="🔒",
    layout="centered",
    initial_sidebar_state="collapsed"
)


if "logged_in" not in st.session_state:
    st.session_state.logged_in = False


if "username" not in st.session_state:
    st.session_state.username = ""


if "role" not in st.session_state:
    st.session_state.role = ""


def login_page():
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("## Multi-Domain Intelligence Platform")
        st.markdown("---")
        
        tab1, tab2 = st.tabs(["Login", "Register"])
        
        with tab1:
            st.subheader("Welcome Back")
            
            with st.form("login_form"):
                username = st.text_input(
                    "Username",
                    placeholder="Enter your username",
                    key="login_username"
                )
                password = st.text_input(
                    "Password",
                    type="password",
                    placeholder="Enter your password",
                    key="login_password"
                )
                
                submit_button = st.form_submit_button(
                    "Login",
                    use_container_width=True
                )
                
                if submit_button:
                    if not username or not password:
                        st.error("Username and password are required")
                    else:
                        success, message = login_user(username, password)
                        
                        if success:
                            st.session_state.logged_in = True
                            st.session_state.username = username
                            st.session_state.role = message
                            st.success(f"Login successful! Welcome, {username}!")
                            st.rerun()
                        else:
                            st.error(f"{message}")
            
            st.markdown("---")
            st.markdown("Don't have an account? Switch to Register tab ->")
        
        with tab2:
            st.subheader("Create New Account")
            
            with st.form("register_form"):
                new_username = st.text_input(
                    "Username",
                    placeholder="Choose a username (3-20 characters)",
                    key="register_username"
                )
                
                new_password = st.text_input(
                    "Password",
                    type="password",
                    placeholder="Create a strong password (6+ characters)",
                    key="register_password"
                )
                
                confirm_password = st.text_input(
                    "Confirm Password",
                    type="password",
                    placeholder="Re-enter your password",
                    key="confirm_password"
                )
                
                role = st.selectbox(
                    "Select Role",
                    ["user", "analyst", "admin"],
                    key="select_role"
                )
                
                submit_reg = st.form_submit_button(
                    "Register",
                    use_container_width=True
                )
                
                if submit_reg:
                    if not new_username or not new_password:
                        st.error("All fields are required")
                    elif len(new_username) < 3 or len(new_username) > 20:
                        st.error("Username must be 3-20 characters")
                    elif len(new_password) < 6:
                        st.error("Password must be at least 6 characters")
                    elif new_password != confirm_password:
                        st.error("Passwords do not match")
                    else:
                        success, message = register_user(
                            new_username,
                            new_password,
                            role
                        )
                        
                        if success:
                            st.success(f"{message}")
                            st.info("You can now log in with your credentials")
                        else:
                            st.error(f"{message}")
            
            st.markdown("---")
            st.markdown("Secure Authentication with bcrypt - Week 9 Streamlit")


def dashboard_page():
    with st.sidebar:
        st.write(f"User: {st.session_state.username}")
        st.write(f"Role: {st.session_state.role.upper()}")
        st.divider()
        
        if st.button("Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.session_state.role = ""
            st.rerun()
    
    st.title("Multi-Domain Intelligence Platform")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Users", "1,000", "+50")
    
    with col2:
        st.metric("Incidents", "156", "-12")
    
    with col3:
        st.metric("IT Tickets", "342", "+18")
    
    st.divider()
    
    st.subheader("Dashboard Navigation")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Dashboard", use_container_width=True):
            st.info("Navigate to Dashboard")
    
    with col2:
        if st.button("📈 Analytics", use_container_width=True):
            st.info("Navigate to Analytics")
    
    with col3:
        if st.button("⚙ Settings", use_container_width=True):
            st.info("Navigate to Settings")
    
    st.divider()
    
    st.subheader("Recent Activity")
    
    sample_data = {
        "Timestamp": ["2025-12-05 16:10", "2025-12-05 16:05", "2025-12-05 16:00"],
        "Event": ["Login", "Dashboard View", "Data Export"],
        "Status": ["Success", "Success", "Pending"]
    }
    
    df = pd.DataFrame(sample_data)
    st.dataframe(df, use_container_width=True)


def main():
    if st.session_state.logged_in:
        dashboard_page()
    else:
        login_page()


if __name__ == "__main__":
    main()