from loguru import logger
from aiogram import types

from modules.schedules import speed_tests
from initbot import dp


@logger.catch
@dp.message_handler(commands="test", is_admin=True)
async def test_start(message):
    await message.answer('Start speed_test...')
    await speed_tests()


@logger.catch
@dp.message_handler()
async def other_message(message: types.Message):
    """Я не знаю такую команду"""
    await message.answer("I don't know this command.")
