import streamlit as st
import pandas as pd
import plotly.express as px
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.dataset import Dataset

st.set_page_config(page_title="Data Science", page_icon="📊", layout="wide")
st.title("Data Science & Analytics")
st.markdown("---")

if st.session_state.get("current_user") is None:
    st.error("Please log in first!")
    st.stop()

CSV_FILE = "files/datasets_metadata.csv"

@st.cache_data
def load_data():
    """Load datasets from CSV and return list of Dataset objects."""
    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE)
        datasets = []
        for _, row in df.iterrows():
            dataset = Dataset(
                dataset_id=int(row['id']),
                name=str(row['name']),
                source=str(row['source']),
                category=str(row['category']),
                size=int(row['size'])
            )
            datasets.append(dataset)
        return datasets
    return []

def save_data(datasets: list):
    """Save list of Dataset objects to CSV."""
    data = [ds.to_dict() for ds in datasets]
    df = pd.DataFrame(data)
    df.to_csv(CSV_FILE, index=False)
    st.cache_data.clear()

datasets = load_data()
tab1, tab2, tab3 = st.tabs(["View Datasets", "Add Dataset", "Analytics"])

with tab1:
    st.subheader("Available Datasets")
    if len(datasets) > 0:
        all_categories = sorted(set(ds.get_category() for ds in datasets))
        all_sources = sorted(set(ds.get_source() for ds in datasets))
        
        col1, col2 = st.columns(2)
        category_filter = col1.selectbox("Filter by Category", ["All"] + all_categories)
        source_filter = col2.selectbox("Filter by Source", ["All"] + all_sources)
        
        filtered = datasets
        if category_filter != "All":
            filtered = [ds for ds in filtered if ds.get_category() == category_filter]
        if source_filter != "All":
            filtered = [ds for ds in filtered if ds.get_source() == source_filter]
        
        st.write(f"Showing {len(filtered)} dataset(s)")
        st.markdown("---")
        
        for dataset in filtered:
            with st.container(border=True):
                col1, col2, col3, col4 = st.columns([3, 2, 1, 1])
                col1.write(f"### {dataset.get_name()}\nCategory: {dataset.get_category()}\nSource: {dataset.get_source()}")
                col2.metric("Size", f"{dataset.calculate_size_mb():.2f} MB")
                if col3.button("Edit", key=f"edit_{dataset.get_id()}"):
                    st.session_state[f'edit_mode_{dataset.get_id()}'] = True
                if col4.button("Delete", key=f"delete_{dataset.get_id()}"):
                    datasets.remove(dataset)
                    save_data(datasets)
                    st.success("Deleted!")
                    st.rerun()
                
                if st.session_state.get(f'edit_mode_{dataset.get_id()}', False):
                    with st.form(key=f"form_{dataset.get_id()}"):
                        new_name = st.text_input("Name", value=dataset.get_name())
                        new_source = st.selectbox("Source", ["Cloud Storage", "Internal", "Database", "API", "External"],
                                                 index=["Cloud Storage", "Internal", "Database", "API", "External"].index(dataset.get_source()) if dataset.get_source() in ["Cloud Storage", "Internal", "Database", "API", "External"] else 0)
                        new_category = st.selectbox("Category", ["Security", "Performance", "Analytics", "Network", "Compliance"],
                                                   index=["Security", "Performance", "Analytics", "Network", "Compliance"].index(dataset.get_category()) if dataset.get_category() in ["Security", "Performance", "Analytics", "Network", "Compliance"] else 0)
                        new_size = st.number_input("Size (KB)", value=dataset.get_size(), min_value=1)
                        
                        col_a, col_b = st.columns(2)
                        if col_a.form_submit_button("Save"):
                            updated = Dataset(dataset.get_id(), new_name, new_source, new_category, int(new_size))
                            datasets[datasets.index(dataset)] = updated
                            save_data(datasets)
                            st.session_state[f'edit_mode_{dataset.get_id()}'] = False
                            st.success("Updated!")
                            st.rerun()
                        if col_b.form_submit_button("Cancel"):
                            st.session_state[f'edit_mode_{dataset.get_id()}'] = False
                            st.rerun()
    else:
        st.info("No datasets found.")

with tab2:
    st.subheader("Add New Dataset")
    with st.form("add_dataset_form"):
        dataset_name = st.text_input("Dataset Name", placeholder="e.g., Customer Analytics Data")
        col1, col2 = st.columns(2)
        source = col1.selectbox("Data Source", ["Cloud Storage", "Internal", "Database", "API", "External"])
        category = col1.selectbox("Category", ["Security", "Performance", "Analytics", "Network", "Compliance"])
        size_kb = col2.number_input("Size (KB)", min_value=1, value=1000, step=100)
        
        if st.form_submit_button("Add Dataset"):
            if not dataset_name:
                st.error("Please enter a dataset name")
            else:
                new_id = max([ds.get_id() for ds in datasets]) + 1 if datasets else 1
                new_dataset = Dataset(new_id, dataset_name, source, category, int(size_kb))
                datasets.append(new_dataset)
                save_data(datasets)
                st.success(f"Dataset '{dataset_name}' added successfully!")
                st.rerun()

with tab3:
    st.subheader("Dataset Analytics")
    if len(datasets) > 0:
        col1, col2, col3 = st.columns(3)
        total_size = sum(ds.calculate_size_mb() for ds in datasets)
        avg_size = total_size / len(datasets)
        max_size = max(ds.calculate_size_mb() for ds in datasets)
        min_size = min(ds.calculate_size_mb() for ds in datasets)
        categories = len(set(ds.get_category() for ds in datasets))
        
        col1.metric("Total Datasets", len(datasets))
        col1.metric("Total Size", f"{total_size:.2f} MB")
        col2.metric("Avg Size", f"{avg_size:.2f} MB")
        col2.metric("Largest Dataset", f"{max_size:.2f} MB")
        col3.metric("Smallest Dataset", f"{min_size:.2f} MB")
        col3.metric("Categories", categories)
        
        st.markdown("---")
        col_left, col_right = st.columns(2)
        
        with col_left:
            st.subheader("Dataset Sizes")
            size_data = {ds.get_name(): ds.calculate_size_mb() for ds in datasets}
            fig1 = px.bar(x=list(size_data.keys()), y=list(size_data.values()), title='Dataset Sizes (MB)')
            fig1.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig1, use_container_width=True)
            
            st.subheader("Data Sources")
            source_data = {}
            for ds in datasets:
                source_data[ds.get_source()] = source_data.get(ds.get_source(), 0) + 1
            fig2 = px.pie(names=list(source_data.keys()), values=list(source_data.values()), title='Datasets by Source')
            st.plotly_chart(fig2, use_container_width=True)
        
        with col_right:
            st.subheader("Category Distribution")
            cat_data = {}
            for ds in datasets:
                cat_data[ds.get_category()] = cat_data.get(ds.get_category(), 0) + 1
            fig3 = px.bar(x=list(cat_data.keys()), y=list(cat_data.values()), title='Datasets by Category')
            st.plotly_chart(fig3, use_container_width=True)
            
            st.subheader("Dataset Details")
            detail_data = [[ds.get_name(), ds.get_source(), ds.get_category(), f"{ds.calculate_size_mb():.2f}"] for ds in datasets[:10]]
            st.dataframe(pd.DataFrame(detail_data, columns=['Name', 'Source', 'Category', 'Size (MB)']), use_container_width=True, hide_index=True)
        
        st.markdown("---")
        st.subheader("Category vs Source Breakdown")
        cat_source = {}
        for ds in datasets:
            key = (ds.get_category(), ds.get_source())
            cat_source[key] = cat_source.get(key, 0) + 1
        crosstab_data = {}
        for (cat, src), count in cat_source.items():
            if cat not in crosstab_data:
                crosstab_data[cat] = {}
            crosstab_data[cat][src] = count
        st.dataframe(pd.DataFrame(crosstab_data).fillna(0).astype(int), use_container_width=True)
        
        csv_data = pd.DataFrame([ds.to_dict() for ds in datasets]).to_csv(index=False)
        st.download_button("Download Data as CSV", csv_data, file_name="datasets_metadata.csv", mime="text/csv")
    else:
        st.info("No datasets available for analysis.")
