import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
from app.data.db import connect_database
from app.data.schema import create_all_tables

st.set_page_config(
    page_title="Cybersecurity Dashboard",
    page_icon="shield",
    layout="wide"
)

if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.error("Please log in first!")
    st.stop()

with st.sidebar:
    st.write(f"User: {st.session_state.username}")
    st.write(f"Role: {st.session_state.role.upper()}")

st.title("Dashboard")

# Dashboard selection buttons
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("🛡️ Cybersecurity", use_container_width=True):
        st.session_state.dashboard_view = "cybersecurity"
with col2:
    if st.button("🎫 IT Tickets", use_container_width=True):
        st.session_state.dashboard_view = "tickets"
with col3:
    if st.button("📊 Data Science", use_container_width=True):
        st.session_state.dashboard_view = "datascience"

# Initialize dashboard view
if "dashboard_view" not in st.session_state:
    st.session_state.dashboard_view = "cybersecurity"

st.divider()

def load_csv_to_database():
    """Load data from CSV files into database if tables are empty."""
    conn = connect_database()
    cursor = conn.cursor()
    
    # Load cyber incidents
    cursor.execute("SELECT COUNT(*) FROM cyber_incidents")
    count = cursor.fetchone()[0]
    if count == 0:
        csv_path = Path("DATA") / "cyber_incidents.csv"
        if csv_path.exists():
            df = pd.read_csv(csv_path)
            if 'id' in df.columns:
                df = df.drop('id', axis=1)
            df.to_sql('cyber_incidents', conn, if_exists='append', index=False)
            conn.commit()
    
    # Load IT tickets
    cursor.execute("SELECT COUNT(*) FROM it_tickets")
    count = cursor.fetchone()[0]
    if count == 0:
        csv_path = Path("DATA") / "it_tickets.csv"
        if csv_path.exists():
            df = pd.read_csv(csv_path)
            if 'id' in df.columns:
                df = df.drop('id', axis=1)
            df.to_sql('it_tickets', conn, if_exists='append', index=False)
            conn.commit()
    
    # Load datasets metadata
    cursor.execute("SELECT COUNT(*) FROM datasets_metadata")
    count = cursor.fetchone()[0]
    if count == 0:
        csv_path = Path("DATA") / "datasets_metadata.csv"
        if csv_path.exists():
            df = pd.read_csv(csv_path)
            if 'id' in df.columns:
                df = df.drop('id', axis=1)
            df.to_sql('datasets_metadata', conn, if_exists='append', index=False)
            conn.commit()
    
    conn.close()

try:
    from app.data.incidents import get_all_incidents
    
    conn = connect_database()
    create_all_tables(conn)
    conn.close()
    
    load_csv_to_database()
    
    # ========================= CYBERSECURITY DASHBOARD =========================
    if st.session_state.dashboard_view == "cybersecurity":
        st.header("🛡️ Cybersecurity Dashboard")
        
        incidents_df = get_all_incidents()
        
        if incidents_df.empty:
            st.warning("No incidents data available")
        else:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Incidents", len(incidents_df))
            
            with col2:
                critical = len(incidents_df[incidents_df['severity'] == 'critical'])
                st.metric("Critical", critical)
            
            with col3:
                high = len(incidents_df[incidents_df['severity'] == 'high'])
                st.metric("High", high)
            
            with col4:
                resolved = len(incidents_df[incidents_df['status'] == 'resolved'])
                st.metric("Resolved", resolved)
            
            st.divider()
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Incidents by Severity")
                severity_counts = incidents_df['severity'].value_counts()
                fig = px.bar(
                    x=severity_counts.index,
                    y=severity_counts.values,
                    labels={'x': 'Severity', 'y': 'Count'}
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.subheader("Incidents by Status")
                status_counts = incidents_df['status'].value_counts()
                fig = px.pie(
                    values=status_counts.values,
                    names=status_counts.index,
                    title="Status Distribution"
                )
                st.plotly_chart(fig, use_container_width=True)
            
            st.divider()
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Incidents by Type")
                type_counts = incidents_df['incident_type'].value_counts()
                fig = px.bar(
                    x=type_counts.values,
                    y=type_counts.index,
                    labels={'x': 'Count', 'y': 'Incident Type'},
                    orientation='h'
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.subheader("Incidents Timeline")
                incidents_df['date'] = pd.to_datetime(incidents_df['date'])
                timeline_df = incidents_df.groupby(incidents_df['date'].dt.date).size().reset_index()
                timeline_df.columns = ['date', 'count']
                fig = px.line(
                    timeline_df,
                    x='date',
                    y='count',
                    labels={'date': 'Date', 'count': 'Number of Incidents'},
                    markers=True
                )
                st.plotly_chart(fig, use_container_width=True)
            
            st.divider()
            
            with st.expander("View All Incidents"):
                st.dataframe(incidents_df, use_container_width=True)
    
    # ========================= IT TICKETS DASHBOARD =========================
    elif st.session_state.dashboard_view == "tickets":
        st.header("🎫 IT Tickets Dashboard")
        
        conn = connect_database()
        tickets_df = pd.read_sql_query("SELECT * FROM it_tickets", conn)
        conn.close()
        
        if tickets_df.empty:
            st.warning("No IT tickets data available")
        else:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Tickets", len(tickets_df))
            
            with col2:
                open_tickets = len(tickets_df[tickets_df['status'] == 'open'])
                st.metric("Open", open_tickets)
            
            with col3:
                in_progress = len(tickets_df[tickets_df['status'] == 'in_progress'])
                st.metric("In Progress", in_progress)
            
            with col4:
                closed = len(tickets_df[tickets_df['status'] == 'closed'])
                st.metric("Closed", closed)
            
            st.divider()
            
            # System health metrics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("CPU Usage", "67%", delta="+5%")
            
            with col2:
                st.metric("Memory", "8.2 GB", delta="+0.3 GB")
            
            with col3:
                st.metric("Uptime", "99.8%", delta="+0.1%")
            
            st.divider()
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Tickets by Priority")
                priority_counts = tickets_df['priority'].value_counts()
                fig = px.bar(
                    x=priority_counts.index,
                    y=priority_counts.values,
                    labels={'x': 'Priority', 'y': 'Count'}
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.subheader("Tickets by Status")
                status_counts = tickets_df['status'].value_counts()
                fig = px.pie(
                    values=status_counts.values,
                    names=status_counts.index,
                    title="Status Distribution"
                )
                st.plotly_chart(fig, use_container_width=True)
            
            st.divider()
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Tickets Timeline")
                tickets_df['created_date'] = pd.to_datetime(tickets_df['created_date'])
                timeline_df = tickets_df.groupby(tickets_df['created_date'].dt.date).size().reset_index()
                timeline_df.columns = ['date', 'count']
                fig = px.line(
                    timeline_df,
                    x='date',
                    y='count',
                    labels={'date': 'Date', 'count': 'Number of Tickets'},
                    markers=True
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.subheader("Resource Usage Over Time")
                usage = pd.DataFrame({
                    "time": ["00:00", "06:00", "12:00", "18:00", "23:59"],
                    "CPU": [45, 52, 78, 82, 67],
                    "Memory": [6.2, 6.8, 8.5, 9.1, 8.2]
                })
                fig = px.line(
                    usage,
                    x='time',
                    y=['CPU', 'Memory'],
                    labels={'value': 'Usage', 'time': 'Time'},
                    markers=True
                )
                st.plotly_chart(fig, use_container_width=True)
            
            st.divider()
            
            with st.expander("View All Tickets"):
                st.dataframe(tickets_df, use_container_width=True)
    
    # ========================= DATA SCIENCE DASHBOARD =========================
    elif st.session_state.dashboard_view == "datascience":
        st.header("📊 Data Science Dashboard")
        
        conn = connect_database()
        datasets_df = pd.read_sql_query("SELECT * FROM datasets_metadata", conn)
        conn.close()
        
        if datasets_df.empty:
            st.warning("No datasets data available")
        else:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Datasets", len(datasets_df))
            
            with col2:
                security = len(datasets_df[datasets_df['category'] == 'Security'])
                st.metric("Security", security)
            
            with col3:
                analytics = len(datasets_df[datasets_df['category'] == 'Analytics'])
                st.metric("Analytics", analytics)
            
            with col4:
                avg_size = datasets_df['size'].mean()
                st.metric("Avg Size (KB)", f"{avg_size:.1f}")
            
            st.divider()
            
            # Model performance metrics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Accuracy", "94.2%")
            
            with col2:
                st.metric("Precision", "91.8%")
            
            with col3:
                st.metric("Recall", "89.5%")
            
            st.divider()
            
            col1, col2 = st.columns(2)
            
            with col2:
                st.subheader("Datasets by Source")
                source_counts = datasets_df['source'].value_counts()
                fig = px.bar(
                    x=source_counts.index,
                    y=source_counts.values,
                    labels={'x': 'Source', 'y': 'Count'}
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.subheader("Datasets by Category")
                category_counts = datasets_df['category'].value_counts()
                fig = px.pie(
                    values=category_counts.values,
                    names=category_counts.index,
                    title="Category Distribution"
                )
                st.plotly_chart(fig, use_container_width=True)
            
            st.divider()
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Dataset Size Distribution")
                fig = px.histogram(
                    datasets_df,
                    x='size',
                    nbins=20,
                    labels={'size': 'Size (KB)', 'count': 'Number of Datasets'}
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.subheader("Training History")
                history = pd.DataFrame({
                    "epoch": [1, 2, 3, 4, 5],
                    "loss": [0.45, 0.32, 0.24, 0.18, 0.15],
                    "accuracy": [0.78, 0.85, 0.89, 0.92, 0.94]
                })
                fig = px.line(
                    history,
                    x='epoch',
                    y=['loss', 'accuracy'],
                    labels={'value': 'Value', 'epoch': 'Epoch'},
                    markers=True
                )
                st.plotly_chart(fig, use_container_width=True)
            
            st.divider()
            
            with st.expander("View All Datasets"):
                st.dataframe(datasets_df, use_container_width=True)

except Exception as e:
    st.error(f"Error loading data: {str(e)}")