import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from aiogram.fsm.storage.memory import MemoryStorage

from config import API_TOKEN
from models.database import init_db
from services.reminder_service import reminder_loop

from controllers.start_controller import register_start_handlers
from controllers.add_controller import register_add_handlers
from controllers.budget_controller import register_budget_handlers
from controllers.report_controller import register_report_handlers
from controllers.delete_controller import register_delete_handlers
from controllers.remind_controller import register_remind_handlers
from controllers.search_controller import register_search_handlers
from controllers.help_controller import register_help_handlers

from controllers.delete_all_controller import register_delete_all_handlers
async def main():
    logging.basicConfig(level=logging.INFO)
    bot = Bot(token=API_TOKEN)
    await bot.delete_webhook(drop_pending_updates=True)

    init_db()
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)


    register_start_handlers(dp)
    register_add_handlers(dp)
    register_budget_handlers(dp)
    register_report_handlers(dp)
    register_delete_handlers(dp)
    register_remind_handlers(dp)
    register_search_handlers(dp)
    register_help_handlers(dp)
    register_delete_all_handlers(dp)

    commands = [
        BotCommand(command="help", description="Помощь"),
        BotCommand(command="expenses", description="Расходы"),
        BotCommand(command="search", description="Поиск расходов (пример: /search продукты)"),
        BotCommand(command="delete_all", description="Удалить все данные о себе")
    ]
    await bot.set_my_commands(commands)

    asyncio.create_task(reminder_loop(bot))

    logging.info("Bot is up and running…")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
