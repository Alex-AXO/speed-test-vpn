from datetime import date, datetime

from loguru import logger
from aiogram import types

import db.main
from modules import reports
from modules.schedules import speed_tests
from initbot import dp, bot

from config import ADMINS


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
@dp.message_handler(commands="test", is_admin=True)
async def test_start(message):
    await message.answer('Start speed_test...')
    await speed_tests()


@logger.catch
@dp.message_handler(commands="last", is_admin=True)
async def last1(message):
    try:
        days = message.text.split()[1]
    except Exception as e:
        days = 7
    await reports.last_report(days)


@logger.catch
@dp.message_handler(commands="week", is_admin=True)
async def week_func(message):
    try:
        week = message.text.split()[1]
    except Exception as e:
        week = date.today().isocalendar()[1]

    logger.debug(f'week-command | {week=}')
    await reports.week_report(week)


@logger.catch
@dp.message_handler(commands="month", is_admin=True)
async def month_func(message):
    try:
        month = message.text.split()[1]
    except Exception as e:
        month = datetime.now().month

    await bot.send_message(ADMINS[0], f'{month=}')
    logger.debug(f'month-command | {month=}')
    await reports.month_report(month)


# --- --- ---


@logger.catch
@dp.message_handler(commands="help", is_admin=True)
async def help_command(message):
    report = f'''
Проверка в: 00:11, 05:11, 10:11, 15:11, 20:11 (msk, +15 min.).

/add – добавить ключ-сервера
/test – принудительное тестирование
/last 14 – отчёт за последн. 14 дней
/week 21 – отчёт за 21 неделю
/month 3 – отчёт за 3 месяц

Примеры:
/add axo-outline-44 ss://...
'''
    await message.answer(report)


@logger.catch
@dp.message_handler()
async def other_message(message: types.Message):
    """Я не знаю такую команду"""
    await message.answer("I don't know this command.")
