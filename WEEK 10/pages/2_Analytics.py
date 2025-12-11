import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
from app.data.db import connect_database
from openai import OpenAI

st.set_page_config(page_title="Analytics & Reporting", layout="wide")

if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.error("Please log in first!")
    st.info("Go to Home page to login")
    st.stop()

with st.sidebar:
    st.write(f"User: {st.session_state.username}")
    st.write(f"Role: {st.session_state.role.upper()}")

st.title("Analytics & Reporting")

# Initialize OpenAI client
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def load_csv_data():
    conn = connect_database()
    tables = {
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

try:
    conn = connect_database()
    incidents_df = pd.read_sql_query("SELECT * FROM cyber_incidents", conn)
    tickets_df = pd.read_sql_query("SELECT * FROM it_tickets", conn)
    datasets_df = pd.read_sql_query("SELECT * FROM datasets_metadata", conn)
    conn.close()
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Incidents", len(incidents_df))
    col2.metric("Total Tickets", len(tickets_df))
    col3.metric("Total Datasets", len(datasets_df))
    
    st.divider()
    
    tab1, tab2, tab3 = st.tabs(["Incidents", "Tickets", "AI Analysis"])
    
    with tab1:
        st.header("Incident Analysis")
        type_counts = incidents_df['incident_type'].value_counts().reset_index()
        type_counts.columns = ['type', 'count']
        severity_counts = incidents_df['severity'].value_counts().reset_index()
        severity_counts.columns = ['severity', 'count']
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("Incidents by Type")
            fig3 = px.bar(type_counts, x='type', y='count')
            st.plotly_chart(fig3, use_container_width=True)
        
        with col2:
            st.markdown("Severity Breakdown")
            fig4 = px.bar(severity_counts, x='severity', y='count', color='severity')
            st.plotly_chart(fig4, use_container_width=True)
    
    with tab2:
        st.header("Ticket Analysis")
        priority_counts = tickets_df['priority'].value_counts().reset_index()
        priority_counts.columns = ['priority', 'count']
        ticket_status_counts = tickets_df['status'].value_counts().reset_index()
        ticket_status_counts.columns = ['status', 'count']
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("Tickets by Priority")
            fig5 = px.bar(priority_counts, x='priority', y='count', color='priority')
            st.plotly_chart(fig5, use_container_width=True)
        
        with col2:
            st.markdown("Tickets by Status")
            fig6 = px.pie(ticket_status_counts, values='count', names='status')
            st.plotly_chart(fig6, use_container_width=True)
    
    with tab3:
        st.header("AI-Enhanced Analysis")
        
        # Combine all data
        all_entries = []
        for idx, row in incidents_df.iterrows():
            all_entries.append({
                'ID': f"INC-{row['id']}",
                'Type': 'Cybersecurity Incident',
                'Title': row['incident_type'],
                'Details': f"Severity: {row['severity']}, Status: {row['status']}",
                'data': row,
                'domain': 'cybersecurity'
            })
        
        for idx, row in tickets_df.iterrows():
            all_entries.append({
                'ID': f"TKT-{row['id']}",
                'Type': 'IT Ticket',
                'Title': row['title'],
                'Details': f"Priority: {row['priority']}, Status: {row['status']}",
                'data': row,
                'domain': 'tickets'
            })
        
        for idx, row in datasets_df.iterrows():
            all_entries.append({
                'ID': f"DST-{row['id']}",
                'Type': 'Dataset',
                'Title': row['name'],
                'Details': f"Category: {row['category']}, Size: {row['size']} KB",
                'data': row,
                'domain': 'datascience'
            })
        
        all_df = pd.DataFrame(all_entries)
        st.info(f"Total entries available: {len(all_df)} ({len(incidents_df)} incidents + {len(tickets_df)} tickets + {len(datasets_df)} datasets)")
        
        st.dataframe(all_df[['ID', 'Type', 'Title', 'Details']], use_container_width=True)
        
        st.divider()
        
        selected_id = st.selectbox("Select Entry ID", all_df['ID'].tolist())
        
        if st.button("Analyze", type="primary"):
            selected = all_df[all_df['ID'] == selected_id].iloc[0]
            domain = selected['domain']
            data = selected['data']
            
            with st.spinner("Analyzing..."):
                if domain == "cybersecurity":
                    text = f"Type: {data['incident_type']}, Severity: {data['severity']}, Status: {data['status']}, Date: {data['date']}, Description: {data['description']}"
                    system_prompt = "You are a cybersecurity expert. Analyze incidents and provide root cause analysis, immediate actions, prevention measures, and risk assessment."
                    user_prompt = f"Analyze this incident:\n{text}"
                
                elif domain == "tickets":
                    text = f"Title: {data['title']}, Priority: {data['priority']}, Status: {data['status']}, Date: {data['created_date']}"
                    system_prompt = "You are an IT operations expert. Analyze tickets and provide problem diagnosis, troubleshooting steps, and resolution recommendations."
                    user_prompt = f"Analyze this ticket:\n{text}"
                
                elif domain == "datascience":
                    text = f"Name: {data['name']}, Category: {data['category']}, Source: {data['source']}, Size: {data['size']} KB"
                    system_prompt = "You are a data science expert. Analyze datasets and provide quality assessment, analysis methods, and visualization recommendations."
                    user_prompt = f"Analyze this dataset:\n{text}"
                
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.7
                )
                st.success("Analysis Complete!")
                st.markdown(response.choices[0].message.content)

except Exception as e:
    st.error(f"Error loading data: {str(e)}")
    st.info("Please ensure the database is properly initialized and contains data.")
