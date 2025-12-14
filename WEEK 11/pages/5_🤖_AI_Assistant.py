import streamlit as st
from services.database_manager import DatabaseManager
from services.ai_assistant import AIAssistant

st.set_page_config(page_title="AI Assistant", page_icon="🤖", layout="wide")
st.title("AI Assistant & Chatbot")
st.markdown("---")

if st.session_state.get("current_user") is None:
    st.error("Please log in first!")
    st.stop()

ai = AIAssistant()

if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({
        "role": "assistant",
        "content": f"Hello {st.session_state.current_user}! I'm your AI assistant. I can help you with:\n\n"
                   "- Security incident analysis\n"
                   "- Dataset recommendations\n"
                   "- IT ticket prioritization\n"
                   "- General platform queries\n\n"
                   "How can I assist you today?"
    })

with st.sidebar:
    st.subheader("AI Features")
    st.markdown("### Quick Actions")
    
    if st.button("Get Platform Summary"):
        db = DatabaseManager("database/platform.db")
        db.connect()
        try:
            security_count = db.fetch_one("SELECT COUNT(*) FROM security_incidents")[0]
            dataset_count = db.fetch_one("SELECT COUNT(*) FROM datasets")[0]
            ticket_count = db.fetch_one("SELECT COUNT(*) FROM it_tickets")[0]
            
            summary = f"**Platform Summary:**\n\nSecurity Incidents: {security_count}\nDatasets: {dataset_count}\nIT Tickets: {ticket_count}\n"
            st.session_state.messages.append({"role": "assistant", "content": summary})
            st.rerun()
        except Exception as e:
            st.error(f"Error: {e}")
        finally:
            db.close()
    
    if st.button("Security Status"):
        db = DatabaseManager("database/platform.db")
        db.connect()
        try:
            critical = db.fetch_one("SELECT COUNT(*) FROM security_incidents WHERE severity = 'critical' AND status != 'Resolved'")[0]
            high = db.fetch_one("SELECT COUNT(*) FROM security_incidents WHERE severity = 'high' AND status != 'Resolved'")[0]
            
            status = f"**Security Status:**\n\nCritical: {critical} active\nHigh: {high} active\n\n"
            status += "Immediate attention required!" if critical > 0 else "No critical incidents."
            
            st.session_state.messages.append({"role": "assistant", "content": status})
            st.rerun()
        except Exception as e:
            st.error(f"Error: {e}")
        finally:
            db.close()
    
    if st.button("IT Ticket Stats"):
        db = DatabaseManager("database/platform.db")
        db.connect()
        try:
            open_tickets = db.fetch_one("SELECT COUNT(*) FROM it_tickets WHERE status = 'Open'")[0]
            in_progress = db.fetch_one("SELECT COUNT(*) FROM it_tickets WHERE status = 'In Progress'")[0]
            
            stats = f"**IT Ticket Stats:**\n\nOpen: {open_tickets}\nIn Progress: {in_progress}\n\n"
            stats += "High volume of open tickets!" if open_tickets > 5 else "Ticket queue is manageable."
            
            st.session_state.messages.append({"role": "assistant", "content": stats})
            st.rerun()
        except Exception as e:
            st.error(f"Error: {e}")
        finally:
            db.close()
    
    if st.button("Analyze Latest Incidents"):
        db = DatabaseManager("database/platform.db")
        db.connect()
        try:
            rows = db.fetch_all("SELECT id, incident_type, severity, status, description FROM security_incidents ORDER BY id DESC LIMIT 3")
            
            if rows:
                prompt = "Analyze these recent security incidents:\n\n"
                for row in rows:
                    prompt += f"- **{row[1]}** (Severity: {row[2]})\n  Status: {row[3]}\n  Description: {row[4]}\n\n"
                prompt += "Provide a summary and risk assessment."
                
                response = ai.send_message(prompt)
                st.session_state.messages.append({"role": "assistant", "content": f"**Incident Analysis:**\n\n{response}"})
                st.rerun()
            else:
                st.session_state.messages.append({"role": "assistant", "content": "No incidents found to analyze."})
                st.rerun()
        except Exception as e:
            st.error(f"Error: {e}")
        finally:
            db.close()
    
    if st.button("Dataset Recommendations"):
        db = DatabaseManager("database/platform.db")
        db.connect()
        try:
            rows = db.fetch_all("SELECT id, name, size_bytes, rows, source FROM datasets ORDER BY id DESC LIMIT 5")
            
            if rows:
                prompt = "Analyze these datasets and provide recommendations:\n\n"
                for row in rows:
                    size_mb = row[2] / (1024 * 1024)
                    prompt += f"- **{row[1]}** ({size_mb:.2f} MB)\n  Rows: {row[3]:,} | Source: {row[4]}\n\n"
                prompt += "Suggest: 1) Analysis techniques 2) Potential insights 3) Data quality checks"
                
                response = ai.send_message(prompt)
                st.session_state.messages.append({"role": "assistant", "content": f"**Dataset Analysis:**\n\n{response}"})
                st.rerun()
            else:
                st.session_state.messages.append({"role": "assistant", "content": "No datasets found to analyze."})
                st.rerun()
        except Exception as e:
            st.error(f"Error: {e}")
        finally:
            db.close()
    
    if st.button("Prioritize Tickets"):
        db = DatabaseManager("database/platform.db")
        db.connect()
        try:
            rows = db.fetch_all("SELECT id, title, priority, status, assigned_to FROM it_tickets WHERE status != 'Closed' ORDER BY id DESC")
            
            if rows:
                prompt = "Help prioritize these IT support tickets:\n\n"
                for row in rows:
                    prompt += f"- Ticket #{row[0]}: {row[1]}\n  Priority: {row[2]} | Status: {row[3]} | Assigned: {row[4]}\n\n"
                prompt += "Recommend: 1) Which tickets need immediate attention 2) Workload distribution"
                
                response = ai.send_message(prompt)
                st.session_state.messages.append({"role": "assistant", "content": f"**Ticket Prioritization:**\n\n{response}"})
                st.rerun()
            else:
                st.session_state.messages.append({"role": "assistant", "content": "No open tickets to prioritize."})
                st.rerun()
        except Exception as e:
            st.error(f"Error: {e}")
        finally:
            db.close()
    
    st.markdown("---")
    if st.button("Clear Chat History"): st.session_state.messages = []; st.rerun()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask me anything about the platform..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = ai.send_message(prompt)
            st.markdown(response)
    
    st.session_state.messages.append({"role": "assistant", "content": response})

st.markdown("---")
st.info("Tip: Use the sidebar for quick actions and platform insights!")
