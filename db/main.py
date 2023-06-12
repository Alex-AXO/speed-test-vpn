import aiosqlite

from initbot import logger
from config import DB_PATH


@logger.catch
async def get_server_keys():
    """Получение всех ключей (серверов)"""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
                "SELECT key_id, server_name, key "
                "FROM server_keys") as result:
            result = await result.fetchall()
            return result if result else []


@logger.catch
async def add_download_info(key_id, download_speed, time, error=0):
    """Добавление информации о скорости скачивания файла и времени"""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(f"INSERT INTO download_files (key_id, download_speed, time, error) "
                              f"VALUES (?, ?, ?, ?);",
                              (key_id, download_speed, time, error)) as cursor:
            await db.commit()
            result = cursor.lastrowid
            return result


@logger.catch
async def add_new_key(server_name, key):
    """Добавление ключа (сервера)"""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(f"INSERT INTO server_keys (server_name, key) "
                              f"VALUES (?, ?);",
                              (server_name, key)) as cursor:
            await db.commit()
            result = cursor.lastrowid
            return result


@logger.catch
async def add_speedtest_info(key_id, ping, download_speed, upload_speed, error=0):
    """Добавление информации о speedtest-cli"""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(f"INSERT INTO speed_tests (key_id, ping, download_speed, upload_speed, error) "
                              f"VALUES (?, ?, ?, ?, ?);",
                              (key_id, ping, download_speed, upload_speed, error)) as cursor:
            await db.commit()
            result = cursor.lastrowid
            return result
