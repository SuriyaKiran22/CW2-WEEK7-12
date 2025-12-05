import pandas as pd


def insert_dataset(conn, name, source, category, size_mb):
    """Insert a new dataset into the datasets_metadata table."""
    cursor = conn.cursor()
    sql = """
    INSERT INTO datasets_metadata (name, source, category, size_mb)
    VALUES (?, ?, ?, ?)"""
    
    cursor.execute(sql, (name, source, category, size_mb))
    conn.commit()
    return cursor.lastrowid

def get_all_datasets(conn):
    """Return all """
    query = "Select * From datasets_metadata ORDER BY id DESC"
    df = pd.read_sql_query(query, conn)
    return df
    pass

def update_dataset_size(conn, dataset_id, new_size):
    """Update the size of a dataset in the datasets_metadata table."""
    cursor = conn.cursor()
    sql = "UPDATE datasets_metadata SET file_size_mb = ? WHERE id = ?"
    cursor.execute(sql, (new_size, dataset_id))
    conn.commit()
    return cursor.rowcount

def delete_dataset(conn, dataset_id):
    """Delete a dataset by ID."""
    cursor = conn.cursor()
    sql = "DELETE FROM datasets_metadata WHERE id = ?"
    cursor.execute(sql, (dataset_id,))
    conn.commit()
    return cursor.rowcount