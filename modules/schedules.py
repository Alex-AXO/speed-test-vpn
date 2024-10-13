from loguru import logger
import asyncio
import aiohttp

from typing import List, Tuple

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
    logger.debug('Start notify_unavailable_servers()')

    keys = await db.main.get_server_keys()
    unavailable_servers = await check_servers_availability(keys)

    for server_name in unavailable_servers:
        message = f'🛑 Warning! Server {server_name} is unavailable!'
        await bot.send_message(ADMINS[0], message)
        logger.error(message)

    logger.debug('End notify_unavailable_servers()')


async def check_servers_availability(keys: List[Tuple]) -> List[str]:
    tasks = []
    for key_id, server_name, key_value in keys:
        if key_value:
            url = await db.main.get_server_url(server_name)
            if url:
                task = check_server_with_retries(url, server_name)
                tasks.append(task)

    results = await asyncio.gather(*tasks)
    return [server for server, is_available in results if not is_available]


async def check_server_with_retries(url: str, server_name: str, retries: int = 3, delay: int = 7) -> Tuple[str, bool]:
    for attempt in range(retries):
        if await check_server_availability(url):
            return server_name, True
        logger.warning(f"Attempt {attempt + 1}/{retries} failed for server {server_name}")
        if attempt < retries - 1:
            await asyncio.sleep(delay)
    logger.error(f"Server {server_name} is unavailable after {retries} attempts")
    return server_name, False
