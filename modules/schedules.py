from loguru import logger

from modules.speed_test import speed_test_key
from config import FILE
import db


async def speed_tests():
    logger.debug(f'Start')
    logger.debug(f'Test-file: {FILE}')

    keys = await db.main.get_server_keys()
    # print(keys)

    for key in keys:
        key_id = key[0]
        server_name = key[1]
        key = key[2]

        logger.debug(f'{server_name=}, {key_id=}')
        await speed_test_key(key, key_id, server_name)
        logger.debug('')
        # break   # Остановка после проверки первого ключа для тестирования

    logger.debug(f'End')
