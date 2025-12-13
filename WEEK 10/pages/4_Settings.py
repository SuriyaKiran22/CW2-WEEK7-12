import streamlit as st
import bcrypt
from app.data.db import connect_database

st.set_page_config(page_title="Settings", layout="wide")

# Check login
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.error("Please log in first!")
    st.info("Go to Home page to login")
    st.stop()

# Sidebar
with st.sidebar:
    st.write(f"User: {st.session_state.username}")
    st.write(f"Role: {st.session_state.role.upper()}")

st.title("⚙️ Settings")

# Profile Info
st.header("Profile Information")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Username", st.session_state.username)
with col2:
    st.metric("Role", st.session_state.role.upper())
with col3:
    # Get total users count
    conn = connect_database()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    result = cursor.fetchone()
    conn.close()
    if result:
        st.metric("Total Users", result[0])
    else:
        st.metric("Total Users", "N/A")

st.divider()

# Appearance Settings
st.header("Appearance")
col1, col2 = st.columns(2)
with col1:
    theme = st.selectbox("Theme", ["Light", "Dark", "Auto"], index=2)
    st.info(f"Current theme: {theme}")
with col2:
    page_size = st.selectbox("Data Display Rows", [10, 25, 50, 100], index=1)
    st.info(f"Showing {page_size} rows per page")

st.divider()

# Notifications
st.header("Notifications")
col1, col2 = st.columns(2)
with col1:
    email_notif = st.checkbox("Email Notifications", value=True)
    security_alerts = st.checkbox("Security Alerts", value=True)
with col2:
    system_updates = st.checkbox("System Updates", value=False)
    weekly_report = st.checkbox("Weekly Report", value=False)

if st.button("Save Preferences", use_container_width=True):
    st.success("Preferences saved successfully!")

st.divider()

# Change Username
st.header("Change Username")
with st.form("username_form"):
    new_username = st.text_input("New Username")
    confirm_password_1 = st.text_input("Confirm Password", type="password")
    submit_username = st.form_submit_button("Update Username", use_container_width=True)
    
    if submit_username:
        if not new_username or not confirm_password_1:
            st.error("All fields are required")
        elif len(new_username) < 3:
            st.error("Username must be at least 3 characters")
        else:
            conn = connect_database()
            cursor = conn.cursor()
            cursor.execute("SELECT password_hash FROM users WHERE username = ?", (st.session_state.username,))
            result = cursor.fetchone()
            
            if result and bcrypt.checkpw(confirm_password_1.encode('utf-8'), result[0].encode('utf-8')):
                cursor.execute("SELECT username FROM users WHERE username = ?", (new_username,))
                if cursor.fetchone():
                    st.error("Username already exists")
                else:
                    cursor.execute("UPDATE users SET username = ? WHERE username = ?", 
                                 (new_username, st.session_state.username))
                    conn.commit()
                    st.session_state.username = new_username
                    st.success("Username updated!")
                    st.rerun()
            else:
                st.error("Incorrect password")
            conn.close()

st.divider()

# Change Password
st.header("Change Password")
with st.form("password_form"):
    old_password = st.text_input("Current Password", type="password")
    new_password = st.text_input("New Password", type="password")
    confirm_new_password = st.text_input("Confirm New Password", type="password")
    submit_password = st.form_submit_button("Update Password", use_container_width=True)
    
    if submit_password:
        if not old_password or not new_password or not confirm_new_password:
            st.error("All fields are required")
        elif len(new_password) < 6:
            st.error("Password must be at least 6 characters")
        elif new_password != confirm_new_password:
            st.error("New passwords do not match")
        else:
            conn = connect_database()
            cursor = conn.cursor()
            cursor.execute("SELECT password_hash FROM users WHERE username = ?", (st.session_state.username,))
            result = cursor.fetchone()
            
            if result and bcrypt.checkpw(old_password.encode('utf-8'), result[0].encode('utf-8')):
                new_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                cursor.execute("UPDATE users SET password_hash = ? WHERE username = ?", 
                             (new_hash, st.session_state.username))
                conn.commit()
                st.success("Password updated!")
            else:
                st.error("Current password is incorrect")
            conn.close()

st.divider()

# Delete Account
st.header("⚠️ Delete Account")
st.warning("This action cannot be undone!")

with st.form("delete_form"):
    confirm_delete_password = st.text_input("Enter Password to Confirm", type="password")
    submit_delete = st.form_submit_button("Delete Account", use_container_width=True, type="primary")
    
    if submit_delete:
        if not confirm_delete_password:
            st.error("Please enter your password")
        else:
            conn = connect_database()
            cursor = conn.cursor()
            cursor.execute("SELECT password_hash FROM users WHERE username = ?", (st.session_state.username,))
            result = cursor.fetchone()
            
            if result and bcrypt.checkpw(confirm_delete_password.encode('utf-8'), result[0].encode('utf-8')):
                cursor.execute("DELETE FROM users WHERE username = ?", (st.session_state.username,))
                conn.commit()
                conn.close()
                st.session_state.logged_in = False
                st.session_state.username = ""
                st.session_state.role = ""
                st.success("Account deleted")
                st.rerun()
            else:
                st.error("Incorrect password")
                conn.close()

st.divider()

# Logout
if st.button("Logout", use_container_width=True):
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = ""
    st.rerun()
