import sqlite3
from config import DB_PATH

def get_conn():
    conn = sqlite3.connect(DB_PATH, detect_types=sqlite3.PARSE_DECLTYPES)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        amount REAL NOT NULL,
        category TEXT NOT NULL,
        type TEXT CHECK(type IN ('expense','income')) NOT NULL,
        date TEXT NOT NULL,
        comment TEXT
    );
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        monthly_budget REAL DEFAULT 0
    );
    """)
    try:
        c.execute("ALTER TABLE users ADD COLUMN monthly_budget REAL DEFAULT 0;")
    except sqlite3.OperationalError:
        pass

    c.execute("""
    CREATE TABLE IF NOT EXISTS reminders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        time TEXT NOT NULL
    );
    """)

    conn.commit()
    conn.close()
