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
async def get_server_name(key_id):
    """Получение server_name"""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
                "SELECT server_name "
                "FROM server_keys "
                "WHERE key_id = ?", (key_id, )) as result:
            result = await result.fetchone()
            return result if result else None


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


@logger.catch
async def get_download_info_week(days):
    """Получение информации (статистики) за неделю по скачиванию файла по серверам за неделю"""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("""
        SELECT 
            key_id, 
            AVG(download_speed) as avg_speed, 
            AVG(time) as avg_time
        FROM download_files 
        WHERE 
            date_time >= datetime('now', ?) AND 
            error = 0
        GROUP BY key_id;""", (f'-{days} days',)) as result:
            result = await result.fetchall()
            return result if result else []


@logger.catch
async def get_download_errors_week(days):
    """Получение кол-ва ошибок за неделю (по скачиванию файла) по серверам за неделю"""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("""
        SELECT 
            key_id, 
            SUM(CASE WHEN error = 1 THEN 1 ELSE 0 END) as error_count
        FROM download_files 
        WHERE 
            date_time >= datetime('now', ?)
        GROUP BY key_id;""", (f'-{days} days',)) as result:
            result = await result.fetchall()
            return result if result else []


@logger.catch
async def get_speedtest_info_week(days):
    """Получение информации (статистики) за неделю по скачиванию файла по серверам за неделю"""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("""
        SELECT 
            key_id, 
            AVG(ping) as avg_ping,
            AVG(download_speed) as avg_download, 
            AVG(upload_speed) as avg_upload
        FROM speed_tests 
        WHERE 
            date_time >= datetime('now', ?) AND 
            error = 0
        GROUP BY key_id;""", (f'-{days} days',)) as result:
            result = await result.fetchall()
            return result if result else []


@logger.catch
async def get_speedtest_errors_week(days):
    """Получение кол-ва ошибок за неделю (по скачиванию файла) по серверам за неделю"""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("""
        SELECT 
            key_id, 
            SUM(CASE WHEN error = 1 THEN 1 ELSE 0 END) as error_count
        FROM speed_tests 
        WHERE 
            date_time >= datetime('now', ?)
        GROUP BY key_id;""", (f'-{days} days',)) as result:
            result = await result.fetchall()
            return result if result else []
