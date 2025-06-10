import asyncio
import logging
from datetime import datetime, timedelta, date as dt_date

from aiogram import Bot
from aiogram.exceptions import TelegramForbiddenError

from models.reminder import get_all_reminders
from models.user import get_all_users
from models.transaction import get_transactions
from models.user import get_budget

alerted_budget: set[int] = set()
inactivity_alerted: set[int] = set()
inactivity_last_date: dt_date = dt_date.today()


async def reminder_loop(bot: Bot):
    global inactivity_last_date, inactivity_alerted

    inactivity_last_date = dt_date.today()
    inactivity_alerted = set()

    last_checked: tuple[int, int] | None = None

    while True:
        now = datetime.now()
        h, m = now.hour, now.minute

        if dt_date.today() != inactivity_last_date:
            inactivity_last_date = dt_date.today()
            inactivity_alerted.clear()

        if (h, m) != last_checked:
            last_checked = (h, m)
            logging.debug(f"⏰ reminder_loop: проверка в {h:02d}:{m:02d}")

            for rem_id, uid, tstr in get_all_reminders():
                hh, mm = map(int, tstr.split(":"))
                if h == hh and m == mm:
                    try:
                        await bot.send_message(uid, "🔔 Напоминание: не забудьте ввести сегодняшние транзакции.")
                    except TelegramForbiddenError:
                        logging.info(f"Пользователь {uid} заблокировал бота – пропускаем personal reminder.")
                    except Exception as e:
                        logging.warning(f"Ошибка при отправке personal reminder {rem_id} пользователю {uid}: {e}")

            for uid in get_all_users():
                try:
                    budget = get_budget(uid)
                    if budget and budget > 0:
                        month_start = now.replace(day=1).strftime("%Y-%m-%d")
                        rows = get_transactions(uid, month_start, now.strftime("%Y-%m-%d"))
                        total_exp = sum(r["amount"] for r in rows if r["type"] == "expense")
                        remaining = budget - total_exp

                        if total_exp >= 0.8 * budget and uid not in alerted_budget:
                            if remaining < 0:
                                text = f"❗️ Вы вышли за пределы бюджета на {abs(remaining):.2f}₽"
                            else:
                                text = f"⚠️ Вы потратили {total_exp:.2f}₽ из {budget:.2f}₽ бюджета! Осталось {remaining:.2f}₽"

                            try:
                                await bot.send_message(uid, text)
                            except TelegramForbiddenError:
                                logging.info(f"Пользователь {uid} заблокировал бота – пропускаем budget alert.")
                            except Exception as e:
                                logging.warning(f"Ошибка при отправке budget alert пользователю {uid}: {e}")
                            else:
                                alerted_budget.add(uid)
                except Exception as e:
                    logging.warning(f"Ошибка при проверке бюджета для {uid}: {e}")

            cutoff = (now - timedelta(days=3)).strftime("%Y-%m-%d")
            for uid in get_all_users():
                try:
                    all_rows = get_transactions(uid, "0000-01-01", now.strftime("%Y-%m-%d"))
                    if not all_rows:
                        continue

                    recent_rows = get_transactions(uid, cutoff, now.strftime("%Y-%m-%d"))
                    dates = {r["date"] for r in recent_rows}
                    if not dates and uid not in inactivity_alerted:
                        await bot.send_message(uid, "⏳ Вы не вносили транзакции последние 3 дня.")
                        inactivity_alerted.add(uid)
                except Exception as e:
                    logging.warning(f"Ошибка при проверке активности для {uid}: {e}")

        await asyncio.sleep(60)
