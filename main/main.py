from loguru import logger

from config import KEYS, FILE
from modules.speed_test import speed_test_key


logger.add("logs/debug.log", format="{time} - {level} - {message}", level="DEBUG",
           rotation="5 days")  # Запись лог-файлов


@logger.catch
def main():

    logger.debug(f'Start')
    logger.debug(f'Test-file: {FILE}')

    for key in KEYS:
        server = key
        key = KEYS[key]

        logger.debug(f'{server=}')
        speed_test_key(key)
        logger.debug('')
        # break

    logger.debug(f'End')


if __name__ == '__main__':
    main()
