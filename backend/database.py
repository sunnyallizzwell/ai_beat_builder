import sqlite3
import os

DB_FILE = '/app/shared_data/data.db'
os.makedirs('/app/shared_data', exist_ok=True)

def get_db():
    conn = sqlite3.connect(DB_FILE, timeout=10)
    conn.execute('PRAGMA journal_mode=WAL;') # Enables fast async reading/writing
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS queue (link TEXT PRIMARY KEY, status TEXT, track_name TEXT)''')
        conn.execute('''CREATE TABLE IF NOT EXISTS settings (setting_key TEXT PRIMARY KEY, setting_value TEXT)''')
        conn.execute("INSERT OR IGNORE INTO settings (setting_key, setting_value) VALUES ('max_workers', '2')")

init_db()