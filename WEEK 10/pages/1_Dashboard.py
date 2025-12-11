import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
from app.data.db import connect_database
from app.data.schema import create_all_tables

st.set_page_config(page_title="Dashboard", page_icon="shield", layout="wide")

if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.error("Please log in first!")
    st.stop()

with st.sidebar:
    st.write(f"User: {st.session_state.username}")
    st.write(f"Role: {st.session_state.role.upper()}")

st.title("Dashboard")

col1, col2, col3 = st.columns(3)
with col1:
    if st.button("Cybersecurity", use_container_width=True):
        st.session_state.dashboard_view = "cybersecurity"
with col2:
    if st.button("IT Tickets", use_container_width=True):
        st.session_state.dashboard_view = "tickets"
with col3:
    if st.button("Data Science", use_container_width=True):
        st.session_state.dashboard_view = "datascience"

if "dashboard_view" not in st.session_state:
    st.session_state.dashboard_view = "cybersecurity"

st.divider()

def load_csv():
    conn = connect_database()
    cursor = conn.cursor()
    for table, csv_file in {'cyber_incidents': 'cyber_incidents.csv', 'it_tickets': 'it_tickets.csv', 'datasets_metadata': 'datasets_metadata.csv'}.items():
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        if cursor.fetchone()[0] == 0:
            csv_path = Path("DATA") / csv_file
            if csv_path.exists():
                df = pd.read_csv(csv_path)
                if 'id' in df.columns:
                    df = df.drop('id', axis=1)
                df.to_sql(table, conn, if_exists='append', index=False)
    conn.commit()
    conn.close()

try:
    from app.data.incidents import get_all_incidents
    conn = connect_database()
    create_all_tables(conn)
    conn.close()
    load_csv()
    
    conn = connect_database()
    
    if st.session_state.dashboard_view == "cybersecurity":
        st.header("Cybersecurity Dashboard")
        df = get_all_incidents()
        
        if not df.empty:
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total", len(df))
            col2.metric("Critical", len(df[df['severity'] == 'critical']))
            col3.metric("High", len(df[df['severity'] == 'high']))
            col4.metric("Resolved", len(df[df['status'] == 'resolved']))
            
            st.divider()
            col1, col2 = st.columns(2)
            with col1:
                fig = px.bar(x=df['severity'].value_counts().index, y=df['severity'].value_counts().values, title="By Severity")
                st.plotly_chart(fig, use_container_width=True)
            with col2:
                fig = px.pie(values=df['status'].value_counts().values, names=df['status'].value_counts().index, title="By Status")
                st.plotly_chart(fig, use_container_width=True)
            
            st.divider()
            st.dataframe(df, use_container_width=True)
            
            st.divider()
            tab1, tab2, tab3, tab4 = st.tabs(["Create", "Update", "Delete", "View All"])
            
            with tab1:
                with st.form("create"):
                    incident_type = st.text_input("Incident Type")
                    severity = st.selectbox("Severity", ["low", "medium", "high", "critical"])
                    if st.form_submit_button("Create") and incident_type:
                        conn.execute("INSERT INTO cyber_incidents (date, incident_type, severity, status, description, reported_by) VALUES (?, ?, ?, 'open', '', ?)",
                                   (str(pd.Timestamp.now().date()), incident_type, severity, st.session_state.username))
                        conn.commit()
                        st.success("Created!")
                        st.rerun()
            
            with tab2:
                temp_df = pd.read_sql_query("SELECT id, incident_type FROM cyber_incidents", conn)
                if not temp_df.empty:
                    with st.form("update"):
                        incident_id = st.selectbox("ID", temp_df['id'].tolist())
                        new_status = st.selectbox("Status", ["open", "in_progress", "resolved", "closed"])
                        if st.form_submit_button("Update"):
                            conn.execute("UPDATE cyber_incidents SET status=? WHERE id=?", (new_status, incident_id))
                            conn.commit()
                            st.success("Updated!")
                            st.rerun()
            
            with tab3:
                with st.form("delete"):
                    incident_id = st.number_input("ID", min_value=1, step=1)
                    if st.form_submit_button("Delete"):
                        conn.execute("DELETE FROM cyber_incidents WHERE id=?", (incident_id,))
                        conn.commit()
                        st.success("Deleted!")
                        st.rerun()
            
            with tab4:
                st.dataframe(df, use_container_width=True)
    
    elif st.session_state.dashboard_view == "tickets":
        st.header("IT Tickets Dashboard")
        df = pd.read_sql_query("SELECT * FROM it_tickets", conn)
        
        if not df.empty:
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total", len(df))
            col2.metric("Open", len(df[df['status'] == 'open']))
            col3.metric("In Progress", len(df[df['status'] == 'in_progress']))
            col4.metric("Closed", len(df[df['status'] == 'closed']))
            
            st.divider()
            col1, col2 = st.columns(2)
            with col1:
                fig = px.bar(x=df['priority'].value_counts().index, y=df['priority'].value_counts().values, title="By Priority")
                st.plotly_chart(fig, use_container_width=True)
            with col2:
                fig = px.pie(values=df['status'].value_counts().values, names=df['status'].value_counts().index, title="By Status")
                st.plotly_chart(fig, use_container_width=True)
            
            st.divider()
            st.dataframe(df, use_container_width=True)
            
            st.divider()
            tab1, tab2, tab3, tab4 = st.tabs(["Create", "Update", "Delete", "View All"])
            
            with tab1:
                with st.form("create"):
                    title = st.text_input("Title")
                    priority = st.selectbox("Priority", ["low", "medium", "high", "critical"])
                    if st.form_submit_button("Create") and title:
                        conn.execute("INSERT INTO it_tickets (title, priority, status, created_date) VALUES (?, ?, 'open', ?)",
                                   (title, priority, str(pd.Timestamp.now().date())))
                        conn.commit()
                        st.success("Created!")
                        st.rerun()
            
            with tab2:
                temp_df = pd.read_sql_query("SELECT id, title FROM it_tickets", conn)
                if not temp_df.empty:
                    with st.form("update"):
                        ticket_id = st.selectbox("ID", temp_df['id'].tolist())
                        new_status = st.selectbox("Status", ["open", "in_progress", "closed"])
                        if st.form_submit_button("Update"):
                            conn.execute("UPDATE it_tickets SET status=? WHERE id=?", (new_status, ticket_id))
                            conn.commit()
                            st.success("Updated!")
                            st.rerun()
            
            with tab3:
                with st.form("delete"):
                    ticket_id = st.number_input("ID", min_value=1, step=1)
                    if st.form_submit_button("Delete"):
                        conn.execute("DELETE FROM it_tickets WHERE id=?", (ticket_id,))
                        conn.commit()
                        st.success("Deleted!")
                        st.rerun()
            
            with tab4:
                st.dataframe(df, use_container_width=True)
    
    elif st.session_state.dashboard_view == "datascience":
        st.header("Data Science Dashboard")
        df = pd.read_sql_query("SELECT * FROM datasets_metadata", conn)
        
        if not df.empty:
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total", len(df))
            col2.metric("Security", len(df[df['category'] == 'Security']))
            col3.metric("Analytics", len(df[df['category'] == 'Analytics']))
            col4.metric("Avg Size", f"{df['size'].mean():.1f}")
            
            st.divider()
            col1, col2 = st.columns(2)
            with col1:
                fig = px.bar(x=df['source'].value_counts().index, y=df['source'].value_counts().values, title="By Source")
                st.plotly_chart(fig, use_container_width=True)
            with col2:
                fig = px.pie(values=df['category'].value_counts().values, names=df['category'].value_counts().index, title="By Category")
                st.plotly_chart(fig, use_container_width=True)
            
            st.divider()
            st.dataframe(df, use_container_width=True)
            
            st.divider()
            tab1, tab2, tab3, tab4 = st.tabs(["Create", "Update", "Delete", "View All"])
            
            with tab1:
                with st.form("create"):
                    name = st.text_input("Dataset Name")
                    category = st.selectbox("Category", ["Security", "Analytics", "Operations"])
                    if st.form_submit_button("Create") and name:
                        conn.execute("INSERT INTO datasets_metadata (name, category, source, size) VALUES (?, ?, 'Manual', 0)", (name, category))
                        conn.commit()
                        st.success("Created!")
                        st.rerun()
            
            with tab2:
                temp_df = pd.read_sql_query("SELECT id, name FROM datasets_metadata", conn)
                if not temp_df.empty:
                    with st.form("update"):
                        dataset_id = st.selectbox("ID", temp_df['id'].tolist())
                        new_category = st.selectbox("Category", ["Security", "Analytics", "Operations"])
                        if st.form_submit_button("Update"):
                            conn.execute("UPDATE datasets_metadata SET category=? WHERE id=?", (new_category, dataset_id))
                            conn.commit()
                            st.success("Updated!")
                            st.rerun()
            
            with tab3:
                with st.form("delete"):
                    dataset_id = st.number_input("ID", min_value=1, step=1)
                    if st.form_submit_button("Delete"):
                        conn.execute("DELETE FROM datasets_metadata WHERE id=?", (dataset_id,))
                        conn.commit()
                        st.success("Deleted!")
                        st.rerun()
            
            with tab4:
                st.dataframe(df, use_container_width=True)
    
    conn.close()

except Exception as e:
    st.error(f"Error: {str(e)}")