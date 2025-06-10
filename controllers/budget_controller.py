from aiogram import types
from aiogram.filters.state import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from models.user import get_budget, set_budget
from views.keyboards import budget_menu_kb, main_menu_kb
from views.templates import BUDGET_PROMPT_TEXT, INVALID_BUDGET_TEXT, CANCEL_TEXT


class BudgetForm(StatesGroup):
    waiting_budget = State()


async def show_budget(message: types.Message):
    current = get_budget(message.from_user.id)
    if current > 0:
        await message.answer(f"Текущий бюджет: {current:.2f}", reply_markup=budget_menu_kb())
    else:
        await message.answer("Бюджет ещё не установлен.", reply_markup=budget_menu_kb())


async def start_change_budget(message: types.Message, state: FSMContext):
    await message.answer(BUDGET_PROMPT_TEXT, reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(BudgetForm.waiting_budget)


async def handle_set_budget(message: types.Message, state: FSMContext):
    text = message.text.strip()
    if text == "🔙 Назад":
        await state.clear()
        return await message.answer(CANCEL_TEXT, reply_markup=main_menu_kb())

    try:
        amount = float(text.replace(",", "."))
    except ValueError:
        return await message.answer(INVALID_BUDGET_TEXT)

    set_budget(message.from_user.id, amount)
    await message.answer(f"✅ Бюджет установлен: {amount:.2f}", reply_markup=main_menu_kb())
    await state.clear()


def register_budget_handlers(dp):
    dp.message.register(show_budget, lambda m: m.text == "💰 Бюджет")
    dp.message.register(start_change_budget, lambda m: m.text == "Изменить бюджет")
    dp.message.register(handle_set_budget, StateFilter(BudgetForm.waiting_budget))
