import sqlite3
from .database import get_conn


def add_transaction(user_id: int, amount: float, category: str, ttype: str, date: str, comment: str):
    conn = get_conn()
    conn.execute(
        "INSERT INTO transactions(user_id, amount, category, type, date, comment) VALUES (?, ?, ?, ?, ?, ?);",
        (user_id, amount, category, ttype, date, comment)
    )
    conn.commit()
    conn.close()

def get_transactions(user_id: int, start_date: str, end_date: str) -> list[sqlite3.Row]:
    conn = get_conn()
    rows = conn.execute(
        "SELECT id, amount, category, type, date, comment "
        "FROM transactions WHERE user_id = ? AND date BETWEEN ? AND ? ORDER BY date, id;",
        (user_id, start_date, end_date)
    ).fetchall()
    conn.close()
    return rows

def get_transaction_by_id(tx_id: int):
    conn = get_conn()
    r = conn.execute(
        "SELECT id, amount, category, type, date, comment FROM transactions WHERE id = ?;",
        (tx_id,)
    ).fetchone()
    conn.close()
    return r

def get_recent_transactions(user_id: int, limit: int = 5) -> list[tuple]:
    conn = get_conn()
    rows = conn.execute(
        "SELECT id, amount, category, type, date FROM transactions "
        "WHERE user_id = ? ORDER BY date DESC, id DESC LIMIT ?;",
        (user_id, limit)
    ).fetchall()
    conn.close()
    return rows

def delete_transaction(tx_id: int):
    conn = get_conn()
    conn.execute("DELETE FROM transactions WHERE id = ?;", (tx_id,))
    conn.commit()
    conn.close()

def get_last_category(user_id: int, ttype: str) -> str | None:
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        SELECT category
        FROM transactions
        WHERE user_id = ? AND type = ?
        ORDER BY date DESC, id DESC
        LIMIT 1;
    """, (user_id, ttype))
    row = c.fetchone()
    conn.close()
    return row["category"] if row else None

def search_expense_by_keyword(user_id: int, keyword: str) -> list[sqlite3.Row]:
    conn = get_conn()
    rows = conn.execute(
        """
        SELECT id, amount, category, type, date, comment
        FROM transactions
        WHERE user_id = ? AND type = 'expense'
        ORDER BY date DESC, id DESC;
        """,
        (user_id,)
    ).fetchall()
    conn.close()
    keyword_lower = keyword.lower()
    result = []
    for r in rows:
        cat = (r["category"] or "").lower()
        comm = (r["comment"] or "").lower()
        if keyword_lower in cat or keyword_lower in comm:
            result.append(r)
    return result

def delete_all_transactions(user_id: int):
    conn = get_conn()
    conn.execute("DELETE FROM transactions WHERE user_id = ?;", (user_id,))
    conn.commit()
    conn.close()