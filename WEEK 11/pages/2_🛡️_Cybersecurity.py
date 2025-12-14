import streamlit as st
import pandas as pd
import plotly.express as px
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# Import service classes and models
from services.database_manager import DatabaseManager
from models.security_incident import SecurityIncident

st.set_page_config(page_title="Cybersecurity", page_icon="🛡️", layout="wide")
st.title("Cybersecurity Management")
st.markdown("---")

# Check if user is logged in
if st.session_state.get("current_user") is None:
    st.error("Please log in first!")
    st.stop()

# Initialize DatabaseManager
db = DatabaseManager("database/platform.db")
db.connect()

# Helper function to load incidents as SecurityIncident objects
def load_incidents():
    """Load incidents from database and wrap them in SecurityIncident objects."""
    rows = db.fetch_all("SELECT id, incident_type, severity, status, description FROM security_incidents ORDER BY id DESC")
    return [SecurityIncident(row[0], "", row[1], row[2], row[3], row[4], "") for row in rows]

# Create tabs
tab1, tab2, tab3 = st.tabs(["Dashboard", "View Incidents", "Add Incident"])

with tab1:
    st.subheader("Security Dashboard Overview")
    
    try:
        incidents = load_incidents()
        
        if len(incidents) > 0:
            # Using object methods to calculate metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Incidents", len(incidents))
            
            with col2:
                # Using get_severity() method from SecurityIncident
                critical_count = sum(1 for inc in incidents if inc.get_severity() == 'critical')
                st.metric("Critical", critical_count)
            
            with col3:
                # Using get_status() method from SecurityIncident
                open_count = sum(1 for inc in incidents if inc.get_status() == 'Open')
                st.metric("Open", open_count)
            
            with col4:
                resolved_count = sum(1 for inc in incidents if inc.get_status() == 'Resolved')
                st.metric("Resolved", resolved_count)
            
            st.markdown("---")
            
            # Visualizations using object methods
            col_left, col_right = st.columns(2)
            
            with col_left:
                st.subheader("Incidents by Severity")
                # Using get_severity() method
                severity_counts = {}
                for incident in incidents:
                    severity = incident.get_severity()
                    severity_counts[severity] = severity_counts.get(severity, 0) + 1
                
                fig1 = px.pie(
                    names=list(severity_counts.keys()),
                    values=list(severity_counts.values()),
                    title='Severity Distribution'
                )
                st.plotly_chart(fig1, use_container_width=True)
                
                st.subheader("Incidents by Type")
                # Using get_incident_type() method
                type_counts = {}
                for incident in incidents:
                    inc_type = incident.get_incident_type()
                    type_counts[inc_type] = type_counts.get(inc_type, 0) + 1
                
                fig3 = px.bar(
                    x=list(type_counts.keys()),
                    y=list(type_counts.values()),
                    title='Incident Types'
                )
                st.plotly_chart(fig3, use_container_width=True)
            
            with col_right:
                st.subheader("Incidents by Status")
                status_counts = {}
                for incident in incidents:
                    status = incident.get_status()
                    status_counts[status] = status_counts.get(status, 0) + 1
                
                fig2 = px.bar(
                    x=list(status_counts.keys()),
                    y=list(status_counts.values()),
                    title='Status Distribution'
                )
                st.plotly_chart(fig2, use_container_width=True)
                
                st.subheader("Severity Levels")
                # Using get_severity_level() method to show numeric levels
                st.write("**Risk Assessment:**")
                for incident in incidents[:5]:  # Show top 5
                    severity_level = incident.get_severity_level()
                    st.write(f"- {incident.get_incident_type()}: Level {severity_level}/4")
        else:
            st.info("No incidents data available. Add incidents to see dashboard.")
    
    except Exception as e:
        st.error(f"Error loading incidents: {str(e)}")

with tab2:
    st.subheader("Security Incidents List")
    
    try:
        incidents = load_incidents()
        
        if len(incidents) > 0:
            # Filters using object methods
            all_severities = sorted(set(inc.get_severity() for inc in incidents))
            all_statuses = sorted(set(inc.get_status() for inc in incidents))
            all_types = sorted(set(inc.get_incident_type() for inc in incidents))
            
            col1, col2, col3 = st.columns(3)
            with col1:
                severity_filter = st.selectbox("Filter by Severity", ["All"] + all_severities)
            with col2:
                status_filter = st.selectbox("Filter by Status", ["All"] + all_statuses)
            with col3:
                type_filter = st.selectbox("Filter by Type", ["All"] + all_types)
            
            # Apply filters using object methods
            filtered_incidents = incidents
            if severity_filter != "All":
                filtered_incidents = [inc for inc in filtered_incidents if inc.get_severity() == severity_filter]
            if status_filter != "All":
                filtered_incidents = [inc for inc in filtered_incidents if inc.get_status() == status_filter]
            if type_filter != "All":
                filtered_incidents = [inc for inc in filtered_incidents if inc.get_incident_type() == type_filter]
            
            st.write(f"Showing {len(filtered_incidents)} incident(s)")
            st.markdown("---")
            
            # Display incidents using object methods
            for incident in filtered_incidents:
                with st.container(border=True):
                    col1, col2, col3 = st.columns([3, 1, 1])
                    
                    with col1:
                        # Using __str__() method for display
                        st.write(f"### Incident #{incident.get_id()}")
                        st.write(f"**Type:** {incident.get_incident_type()}")
                        st.write(f"**Description:** {incident.get_description()}")
                        st.write(f"**Severity Level:** {incident.get_severity_level()}/4")
                    
                    with col2:
                        st.write(f"**Severity:** {incident.get_severity().upper()}")
                        st.write(f"**Status:** {incident.get_status().upper()}")
                    
                    with col3:
                        # Update button
                        if st.button("Edit", key=f"edit_{incident.get_id()}"):
                            st.session_state[f'edit_mode_{incident.get_id()}'] = True
                        
                        # Delete button using DatabaseManager
                        if st.button("Delete", key=f"delete_{incident.get_id()}"):
                            db.execute_query(
                                "DELETE FROM security_incidents WHERE id = ?",
                                (incident.get_id(),)
                            )
                            st.success(f"Incident #{incident.get_id()} deleted!")
                            st.rerun()
                    
                    # Edit form
                    if st.session_state.get(f'edit_mode_{incident.get_id()}', False):
                        with st.form(key=f"form_{incident.get_id()}"):
                            st.write("**Edit Incident**")
                            new_type = st.selectbox("Type", 
                                ["Malware", "Phishing", "Data Breach", "DDoS", "Ransomware", "Insider Threat", "SQL Injection"],
                                index=["Malware", "Phishing", "Data Breach", "DDoS", "Ransomware", "Insider Threat", "SQL Injection"].index(incident.get_incident_type()) 
                                if incident.get_incident_type() in ["Malware", "Phishing", "Data Breach", "DDoS", "Ransomware", "Insider Threat", "SQL Injection"] else 0
                            )
                            new_severity = st.selectbox("Severity", ["low", "medium", "high", "critical"],
                                index=["low", "medium", "high", "critical"].index(incident.get_severity().lower())
                            )
                            new_status = st.selectbox("Status", ["Open", "In Progress", "Resolved"],
                                index=["Open", "In Progress", "Resolved"].index(incident.get_status()) 
                                if incident.get_status() in ["Open", "In Progress", "Resolved"] else 0
                            )
                            new_description = st.text_area("Description", value=incident.get_description())
                            
                            col_a, col_b = st.columns(2)
                            with col_a:
                                if st.form_submit_button("Save"):
                                    # Using DatabaseManager to update
                                    db.execute_query(
                                        """UPDATE security_incidents 
                                           SET incident_type = ?, severity = ?, status = ?, description = ?
                                           WHERE id = ?""",
                                        (new_type, new_severity, new_status, new_description, incident.get_id())
                                    )
                                    st.session_state[f'edit_mode_{incident.get_id()}'] = False
                                    st.success(f"Incident #{incident.get_id()} updated!")
                                    st.rerun()
                            with col_b:
                                if st.form_submit_button("Cancel"):
                                    st.session_state[f'edit_mode_{incident.get_id()}'] = False
                                    st.rerun()
        else:
            st.info("No incidents found. Add incidents from the 'Add Incident' tab.")
    
    except Exception as e:
        st.error(f"Error loading incidents: {str(e)}")

with tab3:
    st.subheader("Add New Security Incident")
    
    with st.form("add_incident_form"):
        incident_type = st.selectbox("Incident Type",
            ["Malware", "Phishing", "Data Breach", "DDoS", "Ransomware", "Insider Threat", "SQL Injection"]
        )
        
        col1, col2 = st.columns(2)
        with col1:
            severity = st.selectbox("Severity Level", ["low", "medium", "high", "critical"])
        with col2:
            status = st.selectbox("Status", ["Open", "In Progress", "Resolved"])
        
        description = st.text_area("Description", placeholder="Describe the security incident...")
        
        if st.form_submit_button("Add Incident"):
            if description:
                try:
                    # Using DatabaseManager to insert
                    db.execute_query(
                        """INSERT INTO security_incidents (incident_type, severity, status, description)
                           VALUES (?, ?, ?, ?)""",
                        (incident_type, severity, status, description)
                    )
                    st.success("Incident added successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error adding incident: {str(e)}")
            else:
                st.error("Please provide a description")

# Close database connection
db.close()

st.markdown("---")
st.info("Tip: Using OOP pattern with SecurityIncident objects and DatabaseManager service")