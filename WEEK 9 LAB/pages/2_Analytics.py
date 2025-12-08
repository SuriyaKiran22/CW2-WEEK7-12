import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
from app.data.db import connect_database

st.set_page_config(page_title="Analytics & Reporting", page_icon="📊", layout="wide")

# Check login
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.error("⚠️ Please log in first!")
    st.info("👈 Go to Home page to login")
    st.stop()

# Sidebar
with st.sidebar:
    st.write(f"User: {st.session_state.username}")
    st.write(f"Role: {st.session_state.role.upper()}")

st.title("Analytics & Reporting")

# Load CSV data into database
def load_csv_data():
    conn = connect_database()
    tables = {
        'users_data': 'users.csv',
        'cyber_incidents': 'cyber_incidents.csv',
        'it_tickets': 'it_tickets.csv',
        'datasets_metadata': 'datasets_metadata.csv'
    }
    
    for table_name, csv_file in tables.items():
        cursor = conn.cursor()
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
        if not cursor.fetchone():
            csv_path = Path("DATA") / csv_file
            if csv_path.exists():
                df = pd.read_csv(csv_path)
                df.to_sql(table_name, conn, if_exists='replace', index=False)
    
    conn.commit()
    conn.close()

load_csv_data()

# Get data
try:
    conn = connect_database()
    users_df = pd.read_sql_query("SELECT * FROM users_data", conn)
    incidents_df = pd.read_sql_query("SELECT * FROM cyber_incidents", conn)
    tickets_df = pd.read_sql_query("SELECT * FROM it_tickets", conn)
    datasets_df = pd.read_sql_query("SELECT * FROM datasets_metadata", conn)
    conn.close()
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Users", len(users_df))
    with col2:
        st.metric("Total Incidents", len(incidents_df))
    with col3:
        st.metric("Total Tickets", len(tickets_df))
    with col4:
        st.metric("Total Datasets", len(datasets_df))
    
    st.divider()
    
    # Tabs for different categories
    tab1, tab2, tab3 = st.tabs(["Users", "Incidents", "Tickets"])
    
    # ========== USERS TAB ==========
    with tab1:
        st.header("User Analysis")
        
        st.subheader("Users by Role")
        
        # Create two columns for user graphs
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("##### Role Distribution")
            # Button to toggle between chart types
            if 'user_graph1' not in st.session_state:
                st.session_state.user_graph1 = 'pie'
            
            btn_col1, btn_col2 = st.columns(2)
            with btn_col1:
                if st.button("Pie Chart", key="user_pie", use_container_width=True):
                    st.session_state.user_graph1 = 'pie'
            with btn_col2:
                if st.button("Bar Chart", key="user_bar", use_container_width=True):
                    st.session_state.user_graph1 = 'bar'
            
            # Role distribution
            role_counts = users_df['role'].value_counts().reset_index()
            role_counts.columns = ['role', 'count']
            
            if st.session_state.user_graph1 == 'pie':
                fig1 = px.pie(role_counts, values='count', names='role')
                fig1.update_traces(textposition='inside', textinfo='percent+label')
                fig1.update_layout(showlegend=True, height=450, margin=dict(t=0, b=0, l=0, r=0))
            else:
                fig1 = px.bar(role_counts, x='role', y='count', color='role')
                fig1.update_layout(showlegend=False, height=450, margin=dict(t=0, b=0, l=0, r=0))
            
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            st.markdown("##### Role Statistics")
            # Button to toggle between display types
            if 'user_graph2' not in st.session_state:
                st.session_state.user_graph2 = 'table'
            
            btn_col1, btn_col2 = st.columns(2)
            with btn_col1:
                if st.button("Table View", key="user_table", use_container_width=True):
                    st.session_state.user_graph2 = 'table'
            with btn_col2:
                if st.button("Bar Chart", key="user_hbar", use_container_width=True):
                    st.session_state.user_graph2 = 'hbar'
            
            if st.session_state.user_graph2 == 'table':
                st.dataframe(role_counts, use_container_width=True, hide_index=True, height=450)
            else:
                fig2 = px.bar(role_counts, y='role', x='count', orientation='h', color='role')
                fig2.update_layout(showlegend=False, height=450, margin=dict(t=0, b=0, l=0, r=0))
                st.plotly_chart(fig2, use_container_width=True)
    
    # ========== INCIDENTS TAB ==========
    with tab2:
        st.header("Incident Analysis")
        
        # Create two columns for incident graphs
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("##### Incidents by Type")
            # Button to toggle between chart types
            if 'incident_graph1' not in st.session_state:
                st.session_state.incident_graph1 = 'bar'
            
            btn_col1, btn_col2 = st.columns(2)
            with btn_col1:
                if st.button("Bar Chart", key="incident_bar", use_container_width=True):
                    st.session_state.incident_graph1 = 'bar'
            with btn_col2:
                if st.button("Line Chart", key="incident_line", use_container_width=True):
                    st.session_state.incident_graph1 = 'line'
            
            # Get incidents by type
            type_counts = incidents_df['incident_type'].value_counts().reset_index()
            type_counts.columns = ['type', 'count']
            
            if st.session_state.incident_graph1 == 'bar':
                fig3 = px.bar(type_counts, x='type', y='count')
                fig3.update_layout(showlegend=False, height=450, xaxis_tickangle=-45, 
                                  margin=dict(t=0, b=0, l=0, r=0))
            else:
                fig3 = px.line(type_counts, x='type', y='count', markers=True)
                fig3.update_layout(height=450, xaxis_tickangle=-45, 
                                  margin=dict(t=0, b=0, l=0, r=0))
            
            st.plotly_chart(fig3, use_container_width=True)
        
        with col2:
            st.markdown("##### Severity Breakdown")
            # Button to toggle between chart types
            if 'incident_graph2' not in st.session_state:
                st.session_state.incident_graph2 = 'bar'
            
            btn_col1, btn_col2 = st.columns(2)
            with btn_col1:
                if st.button("Bar Chart", key="incident_severity_bar", use_container_width=True):
                    st.session_state.incident_graph2 = 'bar'
            with btn_col2:
                if st.button("Pie Chart", key="incident_pie", use_container_width=True):
                    st.session_state.incident_graph2 = 'pie'
            
            # Severity distribution
            severity_counts = incidents_df['severity'].value_counts().reset_index()
            severity_counts.columns = ['severity', 'count']
            
            if st.session_state.incident_graph2 == 'bar':
                fig4 = px.bar(severity_counts, x='severity', y='count', color='severity')
                fig4.update_layout(showlegend=True, height=450, margin=dict(t=0, b=0, l=0, r=0))
            else:
                fig4 = px.pie(severity_counts, values='count', names='severity')
                fig4.update_layout(height=450, margin=dict(t=0, b=0, l=0, r=0))
            
            st.plotly_chart(fig4, use_container_width=True)
    
    # ========== TICKETS TAB ==========
    with tab3:
        st.header("Ticket Analysis")
        
        # Create two columns for ticket graphs
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("##### Tickets by Priority")
            # Button to toggle between chart types
            if 'ticket_graph1' not in st.session_state:
                st.session_state.ticket_graph1 = 'bar'
            
            btn_col1, btn_col2 = st.columns(2)
            with btn_col1:
                if st.button("Bar Chart", key="ticket_bar", use_container_width=True):
                    st.session_state.ticket_graph1 = 'bar'
            with btn_col2:
                if st.button("Pie Chart", key="ticket_pie", use_container_width=True):
                    st.session_state.ticket_graph1 = 'pie'
            
            # Priority distribution
            priority_counts = tickets_df['priority'].value_counts().reset_index()
            priority_counts.columns = ['priority', 'count']
            
            if st.session_state.ticket_graph1 == 'bar':
                fig5 = px.bar(priority_counts, x='priority', y='count', color='priority')
                fig5.update_layout(showlegend=False, height=450, margin=dict(t=0, b=0, l=0, r=0))
            else:
                fig5 = px.pie(priority_counts, values='count', names='priority')
                fig5.update_layout(height=450, margin=dict(t=0, b=0, l=0, r=0))
            
            st.plotly_chart(fig5, use_container_width=True)
        
        with col2:
            st.markdown("##### Tickets by Status")
            # Button to toggle between chart types
            if 'ticket_graph2' not in st.session_state:
                st.session_state.ticket_graph2 = 'bar'
            
            btn_col1, btn_col2 = st.columns(2)
            with btn_col1:
                if st.button("Bar Chart", key="ticket_status_bar", use_container_width=True):
                    st.session_state.ticket_graph2 = 'bar'
            with btn_col2:
                if st.button("Donut Chart", key="ticket_donut", use_container_width=True):
                    st.session_state.ticket_graph2 = 'donut'
            
            # Status distribution
            ticket_status_counts = tickets_df['status'].value_counts().reset_index()
            ticket_status_counts.columns = ['status', 'count']
            
            if st.session_state.ticket_graph2 == 'bar':
                fig6 = px.bar(ticket_status_counts, x='status', y='count', color='status')
                fig6.update_layout(showlegend=False, height=450, margin=dict(t=0, b=0, l=0, r=0))
            else:
                fig6 = px.pie(ticket_status_counts, values='count', names='status', hole=0.4)
                fig6.update_layout(height=450, margin=dict(t=0, b=0, l=0, r=0))
            
            st.plotly_chart(fig6, use_container_width=True)

except Exception as e:
    st.error(f"Error loading data: {str(e)}")
    st.info("Please ensure the database is properly initialized and contains data.")
