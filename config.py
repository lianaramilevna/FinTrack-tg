import os

API_TOKEN = os.getenv("TELEGRAM_TOKEN", "7993334227:AAEcxZqI33XteaRenqjqbrYQxMcbuJGsQ6A")
DB_PATH = os.getenv("DB_PATH", "data/bot.db")
REMIND_CHECK_INTERVAL = 30

os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
