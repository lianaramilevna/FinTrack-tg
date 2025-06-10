from aiogram import types
from aiogram.filters.state import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters.callback_data import CallbackData

from models.reminder import (
    add_reminder,
    get_reminders,
    get_user_reminders,
    delete_reminder
)
from views.keyboards import remind_menu_kb, main_menu_kb
from views.templates import (
    REMIND_TIME_PROMPT_TEXT,
    INVALID_TIME_TEXT,
    CANCEL_TEXT
)


class RemindForm(StatesGroup):
    waiting_time = State()


class RemCallback(CallbackData, prefix="rem"):
    rem_id: int


async def remind_menu(message: types.Message):
    await message.answer("Напоминания:", reply_markup=remind_menu_kb())


async def set_reminder_time(message: types.Message, state: FSMContext):
    text = message.text.strip()
    if text == "Установить время":
        await message.answer(REMIND_TIME_PROMPT_TEXT, reply_markup=types.ReplyKeyboardRemove())
        return await state.set_state(RemindForm.waiting_time)

    if await state.get_state() == RemindForm.waiting_time.state:
        if text == "🔙 Назад":
            await state.clear()
            return await message.answer(CANCEL_TEXT, reply_markup=main_menu_kb())
        from datetime import datetime
        try:
            datetime.strptime(text, "%H:%M")
        except ValueError:
            return await message.answer(INVALID_TIME_TEXT)
        add_reminder(message.from_user.id, text)
        await message.answer(f"Напоминание установлено на {text}", reply_markup=main_menu_kb())
        return await state.clear()


async def show_reminders(message: types.Message):
    times = get_reminders(message.from_user.id)
    if not times:
        text = "У вас нет напоминаний."
    else:
        text = "Ваши напоминания:\n" + "\n".join(f"– {t}" for t in times)
    await message.answer(text, reply_markup=main_menu_kb())


async def delete_reminder_menu(message: types.Message):
    user_id = message.from_user.id
    user_rems = get_user_reminders(user_id)

    if not user_rems:
        return await message.answer("У вас нет напоминаний для удаления.", reply_markup=main_menu_kb())

    buttons = []
    for rem_id, t in user_rems:
        buttons.append([
            types.InlineKeyboardButton(
                text=f"❌ {t}",
                callback_data=RemCallback(rem_id=rem_id).pack()
            )
        ])
    buttons.append([types.InlineKeyboardButton(text="🔙 Отмена", callback_data="cancel_rem")])

    kb = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    await message.answer("Выберите напоминание для удаления:", reply_markup=kb)


async def confirm_remove(callback: types.CallbackQuery, callback_data: RemCallback):
    delete_reminder(callback_data.rem_id)
    await callback.answer("Напоминание удалено.", show_alert=False)
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer("Выберите действие:", reply_markup=main_menu_kb())


async def cancel_remove(callback: types.CallbackQuery):
    await callback.answer("Отмена.", show_alert=False)
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer("Выберите действие:", reply_markup=main_menu_kb())


def register_remind_handlers(dp):
    dp.message.register(remind_menu, lambda m: m.text == "⏰ Напоминания")
    dp.message.register(set_reminder_time, lambda m: m.text == "Установить время")
    dp.message.register(set_reminder_time, StateFilter(RemindForm.waiting_time))
    dp.message.register(show_reminders, lambda m: m.text == "Показать напоминания")
    dp.message.register(delete_reminder_menu, lambda m: m.text == "Удалить напоминание")
    dp.callback_query.register(confirm_remove, RemCallback.filter())
    dp.callback_query.register(cancel_remove, lambda c: c.data == "cancel_rem")
