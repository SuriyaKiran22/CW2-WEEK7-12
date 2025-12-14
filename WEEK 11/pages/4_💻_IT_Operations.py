import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.it_ticket import ITTicket

st.set_page_config(page_title="IT Operations", page_icon="💻", layout="wide")
st.title("IT Operations & Support")
st.markdown("---")

if st.session_state.get("current_user") is None:
    st.error("Please log in first!")
    st.stop()

CSV_FILE = "files/it_tickets.csv"

@st.cache_data
def load_data():
    """Load tickets from CSV and return list of ITTicket objects."""
    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE)
        tickets = []
        for _, row in df.iterrows():
            ticket = ITTicket(
                ticket_id=int(row['id']),
                title=str(row['title']),
                priority=str(row['priority']),
                status=str(row['status']),
                created_date=str(row['created_date'])
            )
            tickets.append(ticket)
        return tickets
    return []

def save_data(tickets: list):
    """Save list of ITTicket objects to CSV."""
    data = [ticket.to_dict() for ticket in tickets]
    df = pd.DataFrame(data)
    df.to_csv(CSV_FILE, index=False)
    st.cache_data.clear()

tickets = load_data()
tab1, tab2, tab3 = st.tabs(["View Tickets", "Create Ticket", "Analytics"])

with tab1:
    st.subheader("IT Support Tickets")
    if len(tickets) > 0:
        all_statuses = sorted(set(t.get_status() for t in tickets))
        all_priorities = sorted(set(t.get_priority() for t in tickets))
        
        col1, col2 = st.columns(2)
        status_filter = col1.selectbox("Filter by Status", ["All"] + all_statuses)
        priority_filter = col2.selectbox("Filter by Priority", ["All"] + all_priorities)
        
        filtered = tickets
        if status_filter != "All":
            filtered = [t for t in filtered if t.get_status() == status_filter]
        if priority_filter != "All":
            filtered = [t for t in filtered if t.get_priority() == priority_filter]
        
        st.write(f"Showing {len(filtered)} ticket(s)")
        st.markdown("---")
        
        for ticket in filtered:
            with st.container(border=True):
                col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                col1.write(f"### Ticket #{ticket.get_id()}\n**{ticket.get_title()}**\nCreated: {ticket.get_created_date()}")
                col2.write(f"**{ticket.get_priority().upper()}**")
                col3.write(f"**{ticket.get_status().upper()}**")
                if col4.button("Edit", key=f"edit_{ticket.get_id()}"):
                    st.session_state[f'edit_mode_{ticket.get_id()}'] = True
                if col4.button("Delete", key=f"delete_{ticket.get_id()}"):
                    tickets.remove(ticket)
                    save_data(tickets)
                    st.success("Deleted!")
                    st.rerun()
                
                if st.session_state.get(f'edit_mode_{ticket.get_id()}', False):
                    with st.form(key=f"form_{ticket.get_id()}"):
                        new_title = st.text_input("Title", value=ticket.get_title())
                        new_priority = st.selectbox("Priority", ["low", "medium", "high", "urgent"],
                                                   index=["low", "medium", "high", "urgent"].index(ticket.get_priority()) if ticket.get_priority() in ["low", "medium", "high", "urgent"] else 0)
                        new_status = st.selectbox("Status", ["open", "in-progress", "resolved", "closed"],
                                                 index=["open", "in-progress", "resolved", "closed"].index(ticket.get_status()) if ticket.get_status() in ["open", "in-progress", "resolved", "closed"] else 0)
                        
                        col_a, col_b = st.columns(2)
                        if col_a.form_submit_button("Save"):
                            updated = ITTicket(ticket.get_id(), new_title, new_priority, new_status, ticket.get_created_date())
                            tickets[tickets.index(ticket)] = updated
                            save_data(tickets)
                            st.session_state[f'edit_mode_{ticket.get_id()}'] = False
                            st.success("Updated!")
                            st.rerun()
                        if col_b.form_submit_button("Cancel"):
                            st.session_state[f'edit_mode_{ticket.get_id()}'] = False
                            st.rerun()
    else:
        st.info("No tickets found.")

with tab2:
    st.subheader("Create New Support Ticket")
    with st.form("create_ticket_form"):
        ticket_title = st.text_input("Ticket Title", placeholder="e.g., Network connectivity issues")
        col1, col2 = st.columns(2)
        priority = col1.selectbox("Priority Level", ["low", "medium", "high", "urgent"])
        created_date = col2.date_input("Date Created", value=datetime.now())
        
        if st.form_submit_button("Create Ticket"):
            if not ticket_title:
                st.error("Please enter a ticket title")
            else:
                new_id = max([t.get_id() for t in tickets]) + 1 if tickets else 1
                new_ticket = ITTicket(new_id, ticket_title, priority, 'open', created_date.strftime('%Y-%m-%d'))
                tickets.append(new_ticket)
                save_data(tickets)
                st.success(f"Ticket #{new_id} '{ticket_title}' created successfully!")
                st.rerun()

with tab3:
    st.subheader("IT Operations Analytics")
    if len(tickets) > 0:
        col1, col2, col3, col4 = st.columns(4)
        open_count = sum(1 for t in tickets if t.get_status() == 'open')
        in_prog = sum(1 for t in tickets if t.get_status() == 'in-progress')
        resolved = sum(1 for t in tickets if t.get_status() in ['resolved', 'closed'])
        
        col1.metric("Total Tickets", len(tickets))
        col2.metric("Open Tickets", open_count, f"{(open_count/len(tickets)*100):.1f}%")
        col3.metric("In Progress", in_prog)
        col4.metric("Resolved/Closed", resolved, f"{(resolved/len(tickets)*100):.1f}%")
        
        st.markdown("---")
        col_left, col_right = st.columns(2)
        
        with col_left:
            st.subheader("Tickets by Priority")
            priority_data = {}
            for t in tickets:
                priority_data[t.get_priority()] = priority_data.get(t.get_priority(), 0) + 1
            fig1 = px.pie(names=list(priority_data.keys()), values=list(priority_data.values()), title='Priority Distribution')
            st.plotly_chart(fig1, use_container_width=True)
            
            st.subheader("Tickets Over Time")
            df_time = pd.DataFrame([{'date': t.get_created_date()} for t in tickets])
            df_time['date'] = pd.to_datetime(df_time['date'])
            trend = df_time.groupby(df_time['date'].dt.to_period('M')).size()
            fig3 = px.line(x=trend.index.astype(str), y=trend.values, title='Monthly Trend')
            st.plotly_chart(fig3, use_container_width=True)
        
        with col_right:
            st.subheader("Tickets by Status")
            status_data = {}
            for t in tickets:
                status_data[t.get_status()] = status_data.get(t.get_status(), 0) + 1
            fig2 = px.bar(x=list(status_data.keys()), y=list(status_data.values()), title='Status Distribution')
            st.plotly_chart(fig2, use_container_width=True)
            
            st.subheader("Priority vs Status Breakdown")
            ps_data = {}
            for t in tickets:
                key = (t.get_priority(), t.get_status())
                ps_data[key] = ps_data.get(key, 0) + 1
            crosstab = {}
            for (pri, sta), cnt in ps_data.items():
                if pri not in crosstab:
                    crosstab[pri] = {}
                crosstab[pri][sta] = cnt
            st.dataframe(pd.DataFrame(crosstab).fillna(0).astype(int), use_container_width=True)
        
        st.markdown("---")
        st.subheader("Complete Ticket List")
        ticket_data = [[t.get_id(), t.get_title(), t.get_priority(), t.get_status(), t.get_created_date()] for t in sorted(tickets, key=lambda x: x.get_id(), reverse=True)[:20]]
        st.dataframe(pd.DataFrame(ticket_data, columns=['ID', 'Title', 'Priority', 'Status', 'Created']), use_container_width=True, hide_index=True)
        
        csv_data = pd.DataFrame([t.to_dict() for t in tickets]).to_csv(index=False)
        st.download_button("Download Data as CSV", csv_data, file_name="it_tickets.csv", mime="text/csv")
    else:
        st.info("No tickets available for analysis.")
