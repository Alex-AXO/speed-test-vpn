from datetime import date, datetime

from logger import logger
from aiogram import types

import db.main
from modules import reports
from modules.schedules import speed_tests
from initbot import dp, bot

from config import ADMINS, HOURS


@logger.catch
@dp.message_handler(commands="add", is_admin=True)
async def add_new_key(message: types.Message):
    """Добавление нового ключа сервера: /add axo-outline-44 ss://..."""
    try:
        server_name = message.text.split()[1]
        key = message.text.split()[2]
    except IndexError:
        await message.answer("Error. No user_id and / or bonuses.")
        return
    logger.debug(f'Added new server_key: {server_name=}, {key=}')
    await db.main.add_new_key(server_name, key)
    await bot.send_message(ADMINS[0], f"Server_key added: {server_name}.")


@logger.catch
@dp.message_handler(commands="update", is_admin=True)
async def update_server(message: types.Message):
    """Обновление данных сервера: /update &lt;id&gt; [name] [key]"""
    parts = message.text.split()
    if len(parts) < 2:
        await message.answer("Usage: /update &lt;id&gt; [name] [key]")
        return

    try:
        server_id = int(parts[1])
    except ValueError:
        await message.answer("Server id must be integer")
        return

    new_name = parts[2] if len(parts) >= 3 else None
    new_key = parts[3] if len(parts) >= 4 else None

    if new_name is None and new_key is None:
        await message.answer("Nothing to update")
        return

    await db.main.update_server_info(server_id, new_name, new_key)
    await message.answer("Server info updated")


@logger.catch
@dp.message_handler(commands="test", is_admin=True)
async def test_start(message):
    await message.answer('Start speed_test...')
    await speed_tests()
    await message.answer('Test finished.')


@logger.catch
@dp.message_handler(commands="last", is_admin=True)
async def last1(message):

    try:
        days = message.text.split()[1]

    except Exception:
        days = 7

    await reports.last_report(days)


@logger.catch
@dp.message_handler(commands="week", is_admin=True)
async def week_func(message):
    try:
        week = message.text.split()[1]
    except Exception:
        week = date.today().isocalendar()[1]

    logger.debug(f'week-command | {week=}')
    await reports.week_report(week)


@logger.catch
@dp.message_handler(commands="month", is_admin=True)
async def month_func(message):
    try:
        month = message.text.split()[1]
    except Exception:
        month = datetime.now().month

    await bot.send_message(ADMINS[0], f'{month=}')
    logger.debug(f'month-command | {month=}')
    await reports.month_report(month)


# --- --- ---


@logger.catch
@dp.message_handler(commands="help", is_admin=True)
async def help_command(message):
    report = f'''
Проверка в: {HOURS}:11, {5 + HOURS}:11, {10 + HOURS}:11, {15 + HOURS}:11, {20 + HOURS}:11 (msk, +15 min.).

/add – добавить ключ-сервера
/update &lt;id&gt; [name] [key] – изменить данные сервера
/test – принудительное тестирование
/last 14 – отчёт за последн. 14 дней
/week 24 – отчёт за 24 неделю
/month 3 – отчёт за 3 месяц

Примеры:
/add axo-outline-44 ss://...
/update 5 new-name ss://...
'''
    await message.answer(report)


@logger.catch
@dp.message_handler()
async def other_message(message: types.Message):
    """Я не знаю такую команду"""
    await message.answer("I don't know this command.")
