from loguru import logger

from modules.speed_test import speed_test_key
from config import FILE, MODE, ADMINS
from initbot import dp, bot
import db


@logger.catch
async def speed_tests():
    # logger.debug(f'Start speed-tests...')
    logger.debug(f'Test-file: {FILE}')
    await bot.send_message(ADMINS[0], 'Start speed_tests...\nTakes ~15 min.')

    keys = await db.main.get_server_keys()
    # print(keys)

    for key in keys:
        key_id = key[0]
        server_name = key[1]
        key = key[2]

        logger.debug(f'{server_name=}, {key_id=}')
        await speed_test_key(key, key_id, server_name)
        logger.debug('')
        # if MODE == 2:
        #     break   # Остановка после проверки первого ключа для тестирования

    logger.debug(f'End')


@logger.catch
async def is_new_data():
    logger.debug(f'is_new_data test')

    table = 'speed_tests'
    if not await db.main.check_new_rows(table):
        report = f'No (or small) data was added (for day) to the table: {table}'
        logger.error(report)
        await bot.send_message(ADMINS[0], report)

    table = 'download_files'
    if not await db.main.check_new_rows(table):
        report = f'No (or small) data was added (for day) to the table: {table}'
        logger.error(report)
        await bot.send_message(ADMINS[0], report)
