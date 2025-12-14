import streamlit as st
from services.database_manager import DatabaseManager
from services.auth_manager import AuthManager

st.set_page_config(page_title="Login", page_icon="🔐")

st.title(" Login")
st.markdown("---")

# Initialize database and auth
db = DatabaseManager("database/platform.db")
auth = AuthManager(db)

# Create tabs for Login and Register
tab1, tab2 = st.tabs(["Login", "Register"])

with tab1:
    st.subheader("User Login")
    
    username = st.text_input("Username", key="login_username")
    password = st.text_input("Password", type="password", key="login_password")
    
    if st.button("Login", key="login_button"):
        if not username or not password:
            st.error(" Please enter username and password")
        else:
            user = auth.login_user(username, password)
            if user:
                st.success(f"Login successful! Welcome, {user.get_username()}!")
                st.session_state.current_user = user.get_username()
                st.session_state.current_role = user.get_role()
                st.balloons()
                # Redirect to Home page after successful login
                st.switch_page("Home.py")
            else:
                st.error("Invalid username or password")
    
    st.info("Test credentials: username='alice', password='password123'")

with tab2:
    st.subheader("Create New Account")
    
    new_username = st.text_input("New Username", key="register_username")
    new_password = st.text_input("New Password", type="password", key="register_password")
    new_password_confirm = st.text_input("Confirm Password", type="password", key="register_confirm")
    
    role = st.selectbox("User Role", ["user", "analyst", "admin"], key="register_role")
    
    if st.button("Register", key="register_button"):
        if not new_username or not new_password:
            st.error("Please enter username and password")
        elif new_password != new_password_confirm:
            st.error("Passwords do not match")
        elif len(new_password) < 6:
            st.error("Password must be at least 6 characters")
        else:
            try:
                success = auth.register_user(new_username, new_password, role)
                if success:
                    st.success(f"Account created successfully! You can now login.")
                    st.balloons()
                else:
                    st.error("Username already exists. Please choose a different username.")
            except Exception as e:
                st.error(f"Registration failed: {str(e)}")

st.markdown("---")
st.info("ℹThis is a demo authentication system using SHA256 hashing. For production, use bcrypt.")