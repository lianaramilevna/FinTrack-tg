from .database import get_conn

def add_user(user_id: int):
    conn = get_conn()
    conn.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?);", (user_id,))
    conn.commit()
    conn.close()

def set_budget(user_id: int, amount: float):
    conn = get_conn()
    conn.execute("UPDATE users SET monthly_budget = ? WHERE user_id = ?;", (amount, user_id))
    conn.commit()
    conn.close()

def get_budget(user_id: int) -> float:
    conn = get_conn()
    r = conn.execute("SELECT monthly_budget FROM users WHERE user_id = ?;", (user_id,)).fetchone()
    conn.close()
    return r["monthly_budget"] if r else 0.0

def get_all_users() -> list[int]:
    conn = get_conn()
    rows = conn.execute("SELECT user_id FROM users;").fetchall()
    conn.close()
    return [r["user_id"] for r in rows]

def delete_user(user_id: int):
    conn = get_conn()
    conn.execute("DELETE FROM users WHERE user_id = ?;", (user_id,))
    conn.commit()
    conn.close()