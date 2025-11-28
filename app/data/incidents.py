import sqlite3
import time
import pandas as pd
from app.data.db import connect_database


def insert_incident(date, incident_type, severity, status, description, reported_by=None, conn=None):
    """Insert new incident using all required table columns."""
    close_conn = False
    if conn is None:
        conn = connect_database()
        close_conn = True

    cursor = conn.cursor()

    # Insert filling ALL required table columns
    cursor.execute(
        """
        INSERT INTO cyber_incidents
        (title, date, affiliations, description, response, victims,
         sponsor, incident_type, category, sources_1, sources_2, sources_3,
         severity, status, reported_by, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
        """,
        (
            "New Incident",
            date,
            "N/A",
            description,
            "N/A",
            "N/A",
            "N/A",
            incident_type,
            "General",
            "N/A",
            "N/A",
            "N/A",
            severity,
            status,
            reported_by,
        )
    )

    conn.commit()
    new_id = cursor.lastrowid

    if close_conn:
        conn.close()

    return new_id


def get_all_incidents():
    """Get all incidents as DataFrame."""
    conn = connect_database()
    df = pd.read_sql_query("SELECT * FROM cyber_incidents ORDER BY id DESC", conn)
    conn.close()
    return df


def update_incident_status(conn, incident_id, new_status):
    """Update the status of an incident."""
    cursor = conn.cursor()
    sql = """UPDATE cyber_incidents SET status = ? WHERE id = ?"""
    cursor.execute(sql, (new_status, incident_id))
    conn.commit()
    return cursor.rowcount


def delete_incident(conn, incident_id):
    """Delete an incident by ID."""
    cursor = conn.cursor()
    sql = "DELETE FROM cyber_incidents WHERE id = ?"
    cursor.execute(sql, (incident_id,))
    conn.commit()
    return cursor.rowcount