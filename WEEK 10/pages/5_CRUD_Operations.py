import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="CRUD",
    layout="wide"
)

# Check authentication
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.error("Please log in first!")
    st.stop()

# Sidebar user info
with st.sidebar:
    st.write(f"User: {st.session_state.username}")
    st.write(f"Role: {st.session_state.role.upper()}")

st.title("CRUD Operations in Streamlit")
st.markdown("**Part 1: Create and Read**")

# Initialize session state for records
if "session_state_records" not in st.session_state:
    st.session_state.session_state_records = []

# Create two columns for CREATE and READ
col1, col2 = st.columns(2)

# CREATE - Add New Records
with col1:
    st.markdown("### CREATE - Add New Records")
    st.caption("Use st.form() to collect input and add to session state:")
    
    with st.expander("Create Form", expanded=True):
        # Create form
        with st.form("add_record"):
            name = st.text_input("Name")
            email = st.text_input("Email")
            role = st.selectbox("Role", ["User", "Admin"])
            
            if st.form_submit_button("Add Record"):
                if name and email:
                    record = {"name": name, "email": email, "role": role}
                    st.session_state.session_state_records.append(record)
                    st.success("Record added!")
                    st.rerun()
                else:
                    st.error("Please fill in all fields!")

# READ - Display Records
with col2:
    st.markdown("### READ - Display Records")
    st.caption("Use st.dataframe() or st.table() to display data:")
    
    with st.expander("Display Records", expanded=True):
        # Display all records
        if st.session_state.session_state_records:
            st.subheader("All Records")
            
            # Convert to DataFrame
            import pandas as pd
            df = pd.DataFrame(st.session_state.session_state_records)
            
            # Display interactive table
            st.dataframe(df, width='stretch')
            
            # Or use static table
            # st.table(df)
        else:
            st.info("No records found!")

st.markdown("---")
st.markdown("**Part 2: Update and Delete operations**")

# Create two columns for UPDATE and DELETE
col3, col4 = st.columns(2)

# UPDATE - Modify Records
with col3:
    st.markdown("### UPDATE - Modify Records")
    st.caption("Select a record and update its values:")
    
    with st.expander("Update Form", expanded=True):
        if st.session_state.session_state_records:
            # Select record to update
            names = [f"{r['name']}" for r in st.session_state.session_state_records]
            selected = st.selectbox("Select record", names, key="update_select")
            
            # Find index
            idx = names.index(selected)
            record = st.session_state.session_state_records[idx]
            
            # Update form
            with st.form("update_form"):
                new_email = st.text_input("Email", record["email"])
                new_role = st.selectbox("Role", ["User", "Admin"], 
                                       index=0 if record["role"] == "User" else 1)
                
                if st.form_submit_button("Update"):
                    if new_email:
                        st.session_state.session_state_records[idx]["email"] = new_email
                        st.session_state.session_state_records[idx]["role"] = new_role
                        st.success("Record updated!")
                        st.rerun()
                    else:
                        st.error("Email cannot be empty!")
        else:
            st.info("No records to update!")

# DELETE - Remove Records
with col4:
    st.markdown("### DELETE - Remove Records")
    st.caption("Select and delete records with confirmation:")
    
    with st.expander("Delete Form", expanded=True):
        if st.session_state.session_state_records:
            names = [f"{r['name']}" for r in st.session_state.session_state_records]
            to_delete = st.selectbox("Select record to delete", names, key="delete_select")
            
            if st.button("Delete", type="primary", key="delete_btn"):
                idx = names.index(to_delete)
                st.session_state.session_state_records.pop(idx)
                st.success("Record deleted!")
                st.rerun()
        else:
            st.info("No records to delete!")

# Sidebar controls
with st.sidebar:
    st.markdown("---")
    st.subheader("Data Management")
    
    if st.button("Clear All Records", width='stretch'):
        st.session_state.session_state_records = []
        st.success("All records cleared!")
        st.rerun()
    
    st.markdown("---")
    st.markdown("### Info")
    st.info("**Forms:** Use st.form() to batch input submissions\n\n**Storage:** Session state for learning, database for production\n\n**Validation:** Always validate input before CRUD operations")
    
    # Display record count
    st.metric("Total Records", len(st.session_state.session_state_records))
