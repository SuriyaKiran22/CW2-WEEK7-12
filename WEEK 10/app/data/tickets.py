import pandas as pd
from app.data.db import connect_database


def insert_ticket(id,title,priority,status,created_date=None):
    conn = connect_database()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO it_tickets
        (id, title, priority, status, created_date)
        VALUES (?, ?, ?, ?, ?)
    """, (id, title, priority, status, created_date))
    conn.commit()
    conn.close()


def get_all_tickets():
    conn = connect_database()
    df = pd.read_sql_query(
        "SELECT * FROM it_tickets ORDER BY id DESC",
        conn
    )
    conn.close()
    return df


def update_ticket_status(ticket_id, new_status):
    conn = connect_database()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE it_tickets SET status = ? WHERE ticket_id = ?",
        (new_status, ticket_id)
    )
    conn.commit()
    conn.close()


def delete_ticket(ticket_id):
    conn = connect_database()
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM it_tickets WHERE ticket_id = ?",
        (ticket_id,)
    )
    conn.commit()
    conn.close()
