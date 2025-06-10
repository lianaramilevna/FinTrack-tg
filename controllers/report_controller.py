from aiogram import types
from aiogram.types import BufferedInputFile
from aiogram.fsm.context import FSMContext
from aiogram.filters.state import StateFilter
from aiogram.fsm.state import StatesGroup, State

from services.report_service import (
    build_monthly_diagrams,
    build_top_comments,
    build_csv_report,
    build_common_report
)
from views.keyboards import report_menu_kb, main_menu_kb
from views.templates import CANCEL_TEXT
from services.report_service import build_spending_trends
from aiogram.filters.command import Command

class CustomPeriodForm(StatesGroup):
    waiting_range = State()


async def report_menu(message: types.Message):
    await message.answer("Меню отчётов:", reply_markup=report_menu_kb())


async def handle_diagrams(message: types.Message):
    files = build_monthly_diagrams(message.from_user.id)
    await message.answer_photo(files[0])
    await message.answer_photo(files[1], reply_markup=main_menu_kb())


async def handle_top_comments(message: types.Message):
    text = build_top_comments(message.from_user.id)
    await message.answer(text, reply_markup=main_menu_kb())


async def handle_export_csv(message: types.Message):
    document = build_csv_report(message.from_user.id)
    await message.answer_document(
        document=document,
        caption="Экспорт CSV",
        reply_markup=main_menu_kb()
    )


async def handle_daily_report(message: types.Message):
    text = build_common_report(message.from_user.id, period="day")
    await message.answer(text, reply_markup=main_menu_kb())


async def handle_monthly_report(message: types.Message):
    text = build_common_report(message.from_user.id, period="month")
    await message.answer(text, reply_markup=main_menu_kb())


async def handle_custom_report(message: types.Message, state: FSMContext):
    if message.text == "🔙 Назад":
        await state.clear()
        return await message.answer(CANCEL_TEXT, reply_markup=main_menu_kb())

    await message.answer(
        "Введите диапазон в формате:\nYYYY-MM-DD YYYY-MM-DD",
        reply_markup=types.ReplyKeyboardMarkup(
            keyboard=[[types.KeyboardButton(text="🔙 Назад")]],
            resize_keyboard=True
        )
    )
    await state.set_state(CustomPeriodForm.waiting_range)


async def process_custom_range(message: types.Message, state: FSMContext):
    text = message.text.strip()
    if text == "🔙 Назад":
        await state.clear()
        return await message.answer(CANCEL_TEXT, reply_markup=main_menu_kb())

    try:
        start_str, end_str = text.split()
        from datetime import date
        date.fromisoformat(start_str)
        date.fromisoformat(end_str)
    except Exception:
        return await message.answer("Неверный формат. Попробуйте ещё раз или нажмите «🔙 Назад».")

    report_text = build_common_report(
        message.from_user.id,
        period="custom",
        start=start_str,
        end=end_str
    )
    await message.answer(report_text, reply_markup=main_menu_kb())
    await state.clear()


async def trend_command(message: types.Message):
    file_month, file_week, analysis_text = build_spending_trends(message.from_user.id)
    await message.answer_photo(file_month)
    await message.answer_photo(file_week)
    await message.answer(analysis_text, reply_markup=main_menu_kb())

def register_report_handlers(dp):
    dp.message.register(report_menu, lambda m: m.text == "📊 Отчёт")
    dp.message.register(handle_diagrams, lambda m: m.text == "📈 Диаграммы")
    dp.message.register(handle_top_comments, lambda m: m.text == "📊 Топ-5 по комментариям")
    dp.message.register(handle_daily_report, lambda m: m.text == "📅 Отчёт за день")
    dp.message.register(handle_monthly_report, lambda m: m.text == "📆 Отчёт за месяц")
    dp.message.register(handle_custom_report, lambda m: m.text == "📂 Произвольный период")
    dp.message.register(process_custom_range, StateFilter(CustomPeriodForm.waiting_range))
    dp.message.register(handle_export_csv, lambda m: m.text == "🔄 Экспорт CSV")

    dp.message.register(trend_command, Command(commands=["expenses"]))