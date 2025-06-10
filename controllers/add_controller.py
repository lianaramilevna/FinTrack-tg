from aiogram import types
from aiogram.filters.state import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from datetime import datetime

from models.transaction import add_transaction, get_last_category
from views.keyboards import (
    add_menu_kb,
    date_menu_kb,
    category_menu_kb,
    comment_menu_kb,
    main_menu_kb
)
from views.templates import (
    ENTER_AMOUNT_TEXT,
    ENTER_DATE_CHOICE_TEXT,
    ENTER_MANUAL_DATE_TEXT,
    INVALID_DATE_TEXT,
    ENTER_CATEGORY_TEXT,
    ENTER_MANUAL_CATEGORY_TEXT,
    ENTER_COMMENT_CHOICE_TEXT,
    ENTER_COMMENT_TEXT,
    INVALID_AMOUNT_TEXT,
    CANCEL_TEXT
)


class AddForm(StatesGroup):
    waiting_type = State()
    waiting_amount = State()
    waiting_date_choice = State()
    waiting_manual_date = State()
    waiting_category = State()
    waiting_manual_category = State()
    waiting_comment = State()


async def start_add(message: types.Message, state: FSMContext):
    await message.answer("Выберите тип транзакции:", reply_markup=add_menu_kb())
    await state.set_state(AddForm.waiting_type)


async def process_type(message: types.Message, state: FSMContext):
    t = message.text.lower()
    if t not in ("доход", "расход"):
        return await message.answer("Нажмите «Доход», «Расход»")
    await state.update_data(ttype=("income" if t == "доход" else "expense"))

    await message.answer(ENTER_AMOUNT_TEXT, reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(AddForm.waiting_amount)


async def process_amount(message: types.Message, state: FSMContext):
    text = message.text.strip()
    try:
        amt = float(text.replace(",", "."))
    except ValueError:
        return await message.answer(INVALID_AMOUNT_TEXT)

    await state.update_data(amount=amt)

    await message.answer(ENTER_DATE_CHOICE_TEXT, reply_markup=date_menu_kb())
    await state.set_state(AddForm.waiting_date_choice)


async def process_date_choice(message: types.Message, state: FSMContext):
    text = message.text

    if text == "Сегодня":
        date_str = datetime.now().strftime("%Y-%m-%d")
        await state.update_data(date=date_str)
        data = await state.get_data()
        last_cat = get_last_category(message.from_user.id, data["ttype"])
        await message.answer(ENTER_CATEGORY_TEXT, reply_markup=category_menu_kb(last_cat))
        await state.set_state(AddForm.waiting_category)
        return

    if text == "Ввести вручную":
        await message.answer(ENTER_MANUAL_DATE_TEXT, reply_markup=types.ReplyKeyboardRemove())
        await state.set_state(AddForm.waiting_manual_date)
        return

    try:
        datetime.fromisoformat(text)
        date_str = text
    except ValueError:
        return await message.answer(INVALID_DATE_TEXT)

    await state.update_data(date=date_str)
    data = await state.get_data()
    last_cat = get_last_category(message.from_user.id, data["ttype"])
    await message.answer(ENTER_CATEGORY_TEXT, reply_markup=category_menu_kb(last_cat))
    await state.set_state(AddForm.waiting_category)


async def process_manual_date(message: types.Message, state: FSMContext):
    text = message.text.strip()

    try:
        datetime.fromisoformat(text)
        date_str = text
    except ValueError:
        return await message.answer(INVALID_DATE_TEXT)

    await state.update_data(date=date_str)
    data = await state.get_data()
    last_cat = get_last_category(message.from_user.id, data["ttype"])
    await message.answer(ENTER_CATEGORY_TEXT, reply_markup=category_menu_kb(last_cat))
    await state.set_state(AddForm.waiting_category)


async def process_category(message: types.Message, state: FSMContext):
    text = message.text.strip()

    if text == "Ввести вручную":
        await message.answer(ENTER_MANUAL_CATEGORY_TEXT, reply_markup=types.ReplyKeyboardRemove())
        await state.update_data(category=None)
        await state.set_state(AddForm.waiting_manual_category)
        return

    await state.update_data(category=text)
    await message.answer(ENTER_COMMENT_CHOICE_TEXT, reply_markup=comment_menu_kb())
    await state.set_state(AddForm.waiting_comment)


async def process_manual_category(message: types.Message, state: FSMContext):
    text = message.text.strip()

    await state.update_data(category=text)
    await message.answer(ENTER_COMMENT_CHOICE_TEXT, reply_markup=comment_menu_kb())
    await state.set_state(AddForm.waiting_comment)


async def process_comment_choice(message: types.Message, state: FSMContext):
    text = message.text.strip()

    if text == "Добавить комментарий":
        await message.answer(ENTER_COMMENT_TEXT, reply_markup=types.ReplyKeyboardRemove())
        return

    if text == "Пропустить":
        data = await state.get_data()
        add_transaction(
            message.from_user.id,
            data["amount"],
            data["category"],
            data["ttype"],
            data["date"],
            ""
        )
        await message.answer("✅ Сохранено.", reply_markup=main_menu_kb())
        await state.clear()
        return

    data = await state.get_data()
    comment = text
    add_transaction(
        message.from_user.id,
        data["amount"],
        data["category"],
        data["ttype"],
        data["date"],
        comment
    )
    await message.answer("✅ Сохранено.", reply_markup=main_menu_kb())
    await state.clear()


async def process_manual_comment(message: types.Message, state: FSMContext):
    text = message.text.strip()

    data = await state.get_data()
    comment = text
    add_transaction(
        message.from_user.id,
        data["amount"],
        data["category"],
        data["ttype"],
        data["date"],
        comment
    )
    await message.answer("✅ Сохранено.", reply_markup=main_menu_kb())
    await state.clear()


def register_add_handlers(dp):
    dp.message.register(start_add, lambda m: m.text == "➕ Добавить")
    dp.message.register(process_type, StateFilter(AddForm.waiting_type))
    dp.message.register(process_amount, StateFilter(AddForm.waiting_amount))
    dp.message.register(process_date_choice, StateFilter(AddForm.waiting_date_choice))
    dp.message.register(process_manual_date, StateFilter(AddForm.waiting_manual_date))
    dp.message.register(process_category, StateFilter(AddForm.waiting_category))
    dp.message.register(process_manual_category, StateFilter(AddForm.waiting_manual_category))
    dp.message.register(process_comment_choice, StateFilter(AddForm.waiting_comment))
    dp.message.register(process_manual_comment, StateFilter(AddForm.waiting_comment))
