from loguru import logger
import asyncio

from modules.speed_test import speed_test_key, save_keys_number, check_server_availability
from config import FILE, ADMINS, MODE
from initbot import bot
import db


@logger.catch
async def speed_tests():
    logger.debug('Start speed-tests...')

    # if MODE != 3:
    #     logger.debug(f'Test-file: {FILE}')

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

    logger.debug('End')


@logger.catch
async def is_new_data():
    logger.debug('is_new_data test')

    table = 'speed_tests'
    if not await db.main.check_new_rows(table):
        report = f'No (or small) data was added (for day) to the table: {table}'
        logger.error(report)
        await bot.send_message(ADMINS[0], report)

    # if MODE != 3:
    #     table = 'download_files'
    #     if not await db.main.check_new_rows(table):
    #         report = f'No (or small) data was added (for day) to the table: {table}'
    #         logger.error(report)
    #         await bot.send_message(ADMINS[0], report)


@logger.catch
async def notify_unavailable_servers():
    """Проверяем сервера на доступность"""

    # logger.debug('Start notify_unavailable_servers()')

    keys = await db.main.get_server_keys()

    for key in keys:
        # key_id = key[0]
        server_name = key[1]
        key = key[2]

        # logger.debug(f'{server_name=}, {key_id=}')

        if key:

            url = await db.main.get_server_url(server_name)
            # logger.debug(f'{url=}')

            server_status = await check_server_availability(url)
            # logger.debug(f'{server_status=}')

            if not server_status:
                await asyncio.sleep(7)  # ждём 7 секунд перед повторной проверкой
                second_check_results = await check_server_availability(url)

                if not second_check_results:
                    await asyncio.sleep(7)  # ждём 7 секунд перед повторной проверкой
                    third_check_results = await check_server_availability(url)

                    if not third_check_results:
                        await bot.send_message(ADMINS[0], f'Внимание! Сервер {server_name} не доступен!')
                        logger.error(f'Attention! Server {server_name} is not available!')

        await asyncio.sleep(2)

    # logger.debug('End')
