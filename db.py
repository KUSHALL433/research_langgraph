import sqlite3
from datetime import datetime

DB_NAME = "research_reports.db"

def create_table():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            query TEXT,
            urls TEXT,
            report TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def save_report(query, urls, report):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO reports (query, urls, report)
        VALUES (?, ?, ?)
    """, (query, ",".join(urls), report))
    conn.commit()
    conn.close()

def fetch_reports():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, query, created_at FROM reports ORDER BY created_at DESC")
    data = cursor.fetchall()
    conn.close()
    return data

def fetch_report_details(report_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT query, urls, report FROM reports WHERE id = ?", (report_id,))
    data = cursor.fetchone()
    conn.close()
    return data
