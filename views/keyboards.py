from aiogram import types

def main_menu_kb() -> types.ReplyKeyboardMarkup:
    return types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="➕ Добавить"), types.KeyboardButton(text="📊 Отчёт")],
            [types.KeyboardButton(text="⏰ Напоминания"), types.KeyboardButton(text="💰 Бюджет")],
            [types.KeyboardButton(text="🗑️ Удалить запись")],
        ],
        resize_keyboard=True
    )

def add_menu_kb() -> types.ReplyKeyboardMarkup:
    return types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="Доход"), types.KeyboardButton(text="Расход")],
        ],
        resize_keyboard=True
    )

def date_menu_kb() -> types.ReplyKeyboardMarkup:
    return types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="Сегодня")],
            [types.KeyboardButton(text="Ввести вручную")],
        ],
        resize_keyboard=True
    )

def category_menu_kb(last_category: str | None) -> types.ReplyKeyboardMarkup:
    buttons = []
    if last_category:
        buttons.append([types.KeyboardButton(text=last_category)])
    buttons.append([types.KeyboardButton(text="Ввести вручную")])
    return types.ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

def comment_menu_kb() -> types.ReplyKeyboardMarkup:
    return types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="Добавить комментарий")],
            [types.KeyboardButton(text="Пропустить")],
        ],
        resize_keyboard=True
    )

def budget_menu_kb() -> types.ReplyKeyboardMarkup:
    return types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="Изменить бюджет")],
            [types.KeyboardButton(text="🔙 Назад")],
        ],
        resize_keyboard=True
    )

def report_menu_kb() -> types.ReplyKeyboardMarkup:
    return types.ReplyKeyboardMarkup(
        keyboard=[
            [
                types.KeyboardButton(text="📈 Диаграммы"),
                types.KeyboardButton(text="📊 Топ-5 по комментариям"),
            ],
            [
                types.KeyboardButton(text="📅 Отчёт за день"),
                types.KeyboardButton(text="📆 Отчёт за месяц"),
            ],
            [
                types.KeyboardButton(text="📂 Произвольный период"),
                types.KeyboardButton(text="🔄 Экспорт CSV"),
            ],
            [types.KeyboardButton(text="🔙 Назад")],
        ],
        resize_keyboard=True
    )

def remind_menu_kb() -> types.ReplyKeyboardMarkup:
    return types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="Установить время")],
            [types.KeyboardButton(text="Показать напоминания")],
            [types.KeyboardButton(text="Удалить напоминание")],
            [types.KeyboardButton(text="🔙 Назад")],
        ],
        resize_keyboard=True
    )

