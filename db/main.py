import aiosqlite

from initbot import logger
from config import DB_PATH


@logger.catch
async def get_server_keys():
    """Получение всех ключей (серверов)"""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
                "SELECT key_id, server_id, server_name, key "
                "FROM server_keys ") as result:
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
