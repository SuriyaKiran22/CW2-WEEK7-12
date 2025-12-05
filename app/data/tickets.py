import pandas as pd


def insert_ticket(conn, ticket_id, priority, status, category, subject, description, created_date, resolved_date, assigned_to):
    """Insert a new IT ticket into the it_tickets table."""
    cursor = conn.cursor()
    sql = """INSERT INTO it_tickets (ticket_id, priority, status, category, subject, description, created_date, resolved_date, assigned_to)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"""
    cursor.execute(sql, (ticket_id, priority, status, category, subject, description, created_date, resolved_date, assigned_to))
    conn.commit()
    return cursor.lastrowid

def get_all_tickets_info(conn):
    """Return all IT tickets as a pandas DataFrame."""
    query = "SELECT * FROM it_tickets ORDER BY id DESC"
    df = pd.read_sql_query(query, conn)
    return df
    pass

def update_ticket_status(conn, ticket_id, new_status):
    """Update the status of an IT ticket."""
    cursor = conn.cursor()
    sql = "UPDATE it_tickets SET status = ? WHERE ticket_id = ?"
    cursor.execute(sql, (new_status, ticket_id))
    conn.commit()
    return cursor.rowcount

def delete_ticket(conn, ticket_id):
    """Delete an IT ticket by ticket_id."""
    cursor = conn.cursor()
    sql = "DELETE FROM it_tickets WHERE ticket_id = ?"
    cursor.execute(sql, (ticket_id,))
    conn.commit()
    return cursor.rowcount