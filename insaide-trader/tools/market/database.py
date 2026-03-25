import sqlite3
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv(override=True)

DB = "accounts.db"

with sqlite3.connect(DB) as conn:
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS market (date TEXT PRIMARY KEY, data TEXT)')
    conn.commit()
    
def write_market(date: str, data: dict) -> None:
    data_json = json.dumps(data)
    with sqlite3.connect(DB) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO market (date, data)
            VALUES (?, ?)
            ON CONFLICT(date) DO UPDATE SET data=excluded.data
        ''', (date, data_json))
        conn.commit()


def read_market(date: str) -> dict | None:
    with sqlite3.connect(DB) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT data FROM market WHERE date = ?', (date,))
        row = cursor.fetchone()
        return json.loads(row[0]) if row else None