from loguru import logger
from aiogram import types

import db.main
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
    # await message.answer('Start speed_test...')
    await speed_tests()


@logger.catch
@dp.message_handler()
async def other_message(message: types.Message):
    """Я не знаю такую команду"""
    await message.answer("I don't know this command.")
