from aiogram import types
from aiogram.filters.command import Command

from views.keyboards import main_menu_kb
from views.templates import START_TEXT

from models.user import add_user

async def cmd_start(message: types.Message):
    add_user(message.from_user.id)
    await message.answer(START_TEXT)
    await message.answer("Выберите действие:", reply_markup=main_menu_kb())

async def cmd_back(message: types.Message):
    add_user(message.from_user.id)
    await message.answer("Выберите действие:", reply_markup=main_menu_kb())

def register_start_handlers(dp):
    dp.message.register(cmd_start, Command(commands=["start"]))
    dp.message.register(cmd_back, lambda m: m.text == "🔙 Назад")
