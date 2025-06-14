
import sqlite3

conn = sqlite3.connect("db.sqlite3")
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS accounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    session_path TEXT
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS commands (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id INTEGER,
    command TEXT,
    target_url TEXT,
    status TEXT DEFAULT 'pending'
)
""")

conn.commit()
conn.close()
print("Database initialized.")
