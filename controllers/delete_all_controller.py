from aiogram import types
from aiogram.filters.state import StateFilter
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from models.transaction import delete_all_transactions
from models.reminder import delete_all_reminders_for_user
from models.user import delete_user
from views.keyboards import main_menu_kb
from views.templates import DELETE_ALL

class DeleteAllForm(StatesGroup):
    waiting_confirm = State()


async def start_delete_all(message: types.Message, state: FSMContext):
    await message.answer(DELETE_ALL, reply_markup=None)
    await state.set_state(DeleteAllForm.waiting_confirm)


async def process_delete_all_confirmation(message: types.Message, state: FSMContext):
    text = message.text.strip().lower()
    if text == "да":
        user_id = message.from_user.id

        delete_all_transactions(user_id)
        delete_all_reminders_for_user(user_id)
        delete_user(user_id)

        await message.answer("Все ваши данные удалены.", reply_markup=main_menu_kb())
        await state.clear()
    elif text == "нет":
        await message.answer("Отмена удаления.", reply_markup=main_menu_kb())
        await state.clear()
    else:
        await message.answer("Пожалуйста, ответьте «да» или «нет».")


def register_delete_all_handlers(dp):
    dp.message.register(start_delete_all, lambda m: m.text == "/delete_all")
    dp.message.register(process_delete_all_confirmation, StateFilter(DeleteAllForm.waiting_confirm))
