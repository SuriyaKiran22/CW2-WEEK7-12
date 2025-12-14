import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Multi-Domain Intelligence Platform", page_icon="🌐", layout="wide")
st.title("Multi-Domain Intelligence Platform")
st.markdown("---")

if "current_user" not in st.session_state:
    st.session_state.current_user = None
if "current_role" not in st.session_state:
    st.session_state.current_role = None

if st.session_state.get("current_user") is None:
    st.info("Please log in using the Login page to access the platform.")
    st.markdown("---")
    st.subheader("Welcome to the Platform")
    st.write("""
    This Multi-Domain Intelligence Platform provides integrated tools for:
    
    - **Authentication**: Secure user management and login
    - **Cybersecurity**: Incident tracking and management
    - **Data Science**: Dataset analysis and exploration
    - **IT Operations**: Support ticket management
    - **AI Assistant**: Intelligent conversation and analysis
    """)
    
else:
    st.success(f"Logged in as: **{st.session_state.current_user}** (Role: {st.session_state.current_role})")
    st.markdown("---")
    st.subheader("Overall Dashboard & Statistics")
    
    try:
        cyber_file = "files/cyber_incidents.csv"
        cyber_df = pd.read_csv(cyber_file) if os.path.exists(cyber_file) else pd.DataFrame()
        security_count = len(cyber_df)
        critical_count = len(cyber_df[cyber_df['severity'] == 'critical']) if len(cyber_df) > 0 else 0
        
        dataset_file = "files/datasets_metadata.csv"
        dataset_df = pd.read_csv(dataset_file) if os.path.exists(dataset_file) else pd.DataFrame()
        dataset_count = len(dataset_df)
        total_size = dataset_df['size'].sum() / 1024 if len(dataset_df) > 0 else 0
        
        ticket_file = "files/it_tickets.csv"
        ticket_df = pd.read_csv(ticket_file) if os.path.exists(ticket_file) else pd.DataFrame()
        ticket_count = len(ticket_df)
        open_count = len(ticket_df[ticket_df['status'] == 'open']) if len(ticket_df) > 0 else 0
        
        from services.database_manager import DatabaseManager
        db = DatabaseManager("database/platform.db")
        db.connect()
        user_stats = db.fetch_one("SELECT COUNT(*) FROM users")
        user_count = user_stats[0] if user_stats else 0
        db.close()
        
    except Exception as e:
        st.error(f"Could not load statistics: {e}")
        security_count = critical_count = dataset_count = total_size = ticket_count = open_count = user_count = 0
    
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Security Incidents", security_count, f"{critical_count} Critical")
    col2.metric("Datasets", dataset_count, f"{total_size:.0f} MB Total")
    col3.metric("IT Tickets", ticket_count, f"{open_count} Open")
    col4.metric("Total Users", user_count, "Registered")
    col5.metric("AI Assistant", "Active", "Ready")
    
    st.markdown("---")
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.subheader("Security Overview")
        try:
            if security_count > 0:
                for severity, count in cyber_df['severity'].value_counts().items():
                    st.write(f"**{severity.upper()}**: {count} incidents")
            else:
                st.info("No security incidents recorded")
            
            st.markdown("---")
            st.subheader("IT Operations Overview")
            if ticket_count > 0:
                for priority, count in ticket_df['priority'].value_counts().items():
                    st.write(f"**{priority.upper()}**: {count} tickets")
            else:
                st.info("No IT tickets recorded")
        except Exception as e:
            st.warning(f"Error loading security/IT details: {e}")
    
    with col_right:
        st.subheader("Data Science Overview")
        try:
            if dataset_count > 0:
                st.write("**Top 5 Datasets by Size:**")
                for idx, row in dataset_df.sort_values('size', ascending=False).head(5).iterrows():
                    st.write(f"- **{row['name']}**: {row['size']/1024:.2f} MB")
                
                st.markdown("---")
                st.write("**Category Distribution:**")
                for category, count in dataset_df['category'].value_counts().head(5).items():
                    st.write(f"- **{category}**: {count} datasets")
            else:
                st.info("No datasets recorded")
            
            st.markdown("---")
            st.subheader("System Health")
            st.write("**Data Files**: Connected")
            st.write("**Authentication**: Active")
            st.write("**All Modules**: Operational")
        except Exception as e:
            st.warning(f"Error loading dataset details: {e}")
    
    st.markdown("---")
    st.info("Use the sidebar to navigate to different modules for detailed management.")
    
    if st.button("Logout"):
        st.session_state.current_user = None
        st.session_state.current_role = None
        st.rerun()