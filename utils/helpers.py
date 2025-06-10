from datetime import datetime

def parse_date(text: str) -> str | None:
    try:
        dt = datetime.fromisoformat(text)
        return dt.strftime("%Y-%m-%d")
    except Exception:
        return None

def format_amount(text: str) -> float | None:
    try:
        return float(text.replace(",", "."))
    except Exception:
        return None
