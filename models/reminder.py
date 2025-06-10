from .database import get_conn

def add_reminder(user_id: int, time_str: str):
    conn = get_conn()
    conn.execute(
        "INSERT INTO reminders (user_id, time) VALUES (?, ?);",
        (user_id, time_str)
    )
    conn.commit()
    conn.close()

def get_reminders(user_id: int) -> list[str]:
    conn = get_conn()
    rows = conn.execute("SELECT time FROM reminders WHERE user_id = ? ORDER BY time;", (user_id,)).fetchall()
    conn.close()
    return [r["time"] for r in rows]

def get_user_reminders(user_id: int) -> list[tuple[int, str]]:
    conn = get_conn()
    rows = conn.execute(
        "SELECT id, time FROM reminders WHERE user_id = ? ORDER BY time;",
        (user_id,)
    ).fetchall()
    conn.close()
    return [(r["id"], r["time"]) for r in rows]

def delete_reminder(rem_id: int):
    conn = get_conn()
    conn.execute("DELETE FROM reminders WHERE id = ?;", (rem_id,))
    conn.commit()
    conn.close()

def get_all_reminders() -> list[tuple[int, int, str]]:
    conn = get_conn()
    rows = conn.execute("SELECT id, user_id, time FROM reminders;").fetchall()
    conn.close()
    return [(r["id"], r["user_id"], r["time"]) for r in rows]

def delete_all_reminders_for_user(user_id: int):
    conn = get_conn()
    conn.execute("DELETE FROM reminders WHERE user_id = ?;", (user_id,))
    conn.commit()
    conn.close()