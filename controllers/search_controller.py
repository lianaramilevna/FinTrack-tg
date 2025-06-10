from aiogram import types
from aiogram.filters.command import Command

from models.transaction import search_expense_by_keyword
from views.keyboards import main_menu_kb


async def search_transactions(message: types.Message):
    text = message.text or ""
    parts = text.split(maxsplit=1)

    if len(parts) < 2 or not parts[1].strip():
        return await message.answer(
            "Использование: /search <ключевое_слово>\n"
            "Пример: /search продукты",
            reply_markup=main_menu_kb()
        )

    keyword = parts[1].strip().lower()
    rows = search_expense_by_keyword(message.from_user.id, keyword)

    if not rows:
        return await message.answer(
            f"Расходы, содержащие «{keyword}», не найдены.",
            reply_markup=main_menu_kb()
        )

    lines = [f"🔎 Результаты поиска «{keyword}»:"]
    for r in rows:
        date_str = r["date"]
        cat = r["category"]
        amt = r["amount"]
        comment = r["comment"] or "-"
        lines.append(f"{date_str} | {cat}: {amt:.2f}₽ | Комментарий: {comment}")

    await message.answer("\n".join(lines), reply_markup=main_menu_kb())


def register_search_handlers(dp):
    dp.message.register(search_transactions, Command(commands=["search"]))
