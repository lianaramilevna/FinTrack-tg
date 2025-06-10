from aiogram import types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters.callback_data import CallbackData

from models.transaction import (
    get_recent_transactions,
    get_transaction_by_id,
    delete_transaction
)
from views.keyboards import main_menu_kb


class TxCallback(CallbackData, prefix="tx"):
    tx_id: int


async def start_delete(message: types.Message):
    rows = get_recent_transactions(message.from_user.id, limit=5)
    if not rows:
        return await message.answer("Нет записей.", reply_markup=main_menu_kb())

    kb_rows = []
    for r in rows:
        tx_id, amt, cat, ttype, date = r
        text = f"{date}|{ttype.title()}|{cat}:{amt}"
        kb_rows.append([
            InlineKeyboardButton(
                text=f"❌ {text}",
                callback_data=TxCallback(tx_id=tx_id).pack()
            )
        ])
    kb_rows.append([InlineKeyboardButton(text="🔙 Отмена", callback_data="cancel_delete")])
    await message.answer("Выберите запись:", reply_markup=InlineKeyboardMarkup(inline_keyboard=kb_rows))


async def confirm_delete(callback: types.CallbackQuery, callback_data: TxCallback):
    row = get_transaction_by_id(callback_data.tx_id)
    if not row:
        await callback.answer()
        await callback.message.edit_reply_markup(reply_markup=None)
        return await callback.message.answer("Запись не найдена.", reply_markup=main_menu_kb())

    desc = f"{row['date']}|{row['type'].title()}|{row['category']}:{row['amount']}"
    delete_transaction(callback_data.tx_id)

    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(f"Запись удалена:\n{desc}", reply_markup=main_menu_kb())


async def cancel_delete(callback: types.CallbackQuery):
    await callback.answer("Отмена", show_alert=False)
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer("Главное меню:", reply_markup=main_menu_kb())


def register_delete_handlers(dp):
    dp.message.register(start_delete, lambda m: m.text == "🗑️ Удалить запись")
    dp.callback_query.register(confirm_delete, TxCallback.filter())
    dp.callback_query.register(cancel_delete, lambda c: c.data == "cancel_delete")
