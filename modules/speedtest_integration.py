import subprocess
import asyncio
import re
import json
from logger import logger
import db.main
from config import ERROR_PING, ERROR_SPEED

async def run_async_command(command):
    """Execute command asynchronously and log result"""
    logger.debug(f"Executing: {' '.join(command)}")
    process = await asyncio.create_subprocess_exec(
        *command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()
    if process.returncode == 0:
        logger.debug(f"Success: {' '.join(command)}")
    else:
        logger.error(
            f"Failed ({process.returncode}): {' '.join(command)}\n{stderr.decode().strip()}"
        )
    return process.returncode, stdout.decode(), stderr.decode()

@logger.catch
async def alternative_speed_test_cli(key_id, server_name, localhost=0):
    """Альтернативная функция speedtest через curl для замены speedtest-cli при 403 ошибках"""
    
    logger.debug(f"{server_name}: alternative speedtest started")
    
    if localhost:
        # Для localhost используем ookla-speedtest (как было)
        command = ['./ookla-speedtest', '--accept-license', '--accept-gdpr', '--format=json']
        tool_name = "ookla-speedtest"
        
        try:
            returncode, stdout, stderr = await run_async_command(command)
            if returncode == 0:
                json_start = stdout.find('{"type":')
                if json_start != -1:
                    clean_output = stdout[json_start:]
                    result_data = json.loads(clean_output)
                    ping = round(result_data['ping']['latency'])
                    download_speed = round((result_data['download']['bandwidth'] * 8) / (1024 * 1024), 2)
                    upload_speed = round((result_data['upload']['bandwidth'] * 8) / (1024 * 1024), 2)
                else:
                    raise ValueError("JSON не найден в выводе")
            else:
                raise subprocess.CalledProcessError(returncode, command, stdout, stderr)
                
        except Exception as error:
            logger.error(f"{server_name}: ookla-speedtest failed: {str(error)}")
            await db.main.add_speedtest_info(key_id, 0, 0, 0, 1)
            return
    
    else:
        # Для VPN используем curl через proxychains
        tool_name = "curl-speedtest"
        
        try:
            # 1. Измеряем пинг через curl
            ping = 0
            ping_cmd = ['poetry', 'run', 'proxychains', 'curl', '-o', '/dev/null', '-s', '-w', '%{time_connect}', 'http://httpbin.org/ip']
            returncode, stdout, stderr = await run_async_command(ping_cmd)
            
            if returncode == 0:
                # Извлекаем время соединения из вывода (учитываем ProxyChains префикс)
                time_match = re.search(r'(\d+\.\d+)$', stdout.strip())
                if time_match:
                    ping = round(float(time_match.group(1)) * 1000)  # Convert to ms
            
            # 2. Измеряем скорость загрузки через Linode
            download_speed = 0
            speed_cmd = ['poetry', 'run', 'proxychains', 'curl', '-o', '/dev/null', '-w', '%{speed_download}', 'http://speedtest.atlanta.linode.com/100MB-atlanta.bin']
            returncode, stdout, stderr = await run_async_command(speed_cmd)
            
            if returncode == 0:
                # Извлекаем скорость из вывода (учитываем ProxyChains префикс)
                speed_match = re.search(r'(\d+)$', stdout.strip())
                if speed_match:
                    speed_bytes = float(speed_match.group(1))
                    download_speed = round((speed_bytes * 8) / (1024 * 1024), 2)  # Convert to Mbit/s
            
            # 3. Простая оценка upload (обычно 10-20% от download для VPN)
            upload_speed = round(download_speed * 0.15, 2) if download_speed > 0 else 0
            
        except Exception as error:
            logger.error(f"{server_name}: alternative speedtest failed: {str(error)}")
            await db.main.add_speedtest_info(key_id, 0, 0, 0, 1)
            return
    
    # Логирование результатов в том же формате что и оригинальная функция
    report = (f'{tool_name} result:\n'
              f'{ping=} ms,\n'
              f'{download_speed=} Mbit/s,\n'
              f'{upload_speed=} Mbit/s')
    logger.debug(report)
    
    # Проверка на ошибочные значения (как в оригинале)
    if download_speed < ERROR_SPEED or upload_speed < ERROR_SPEED or ping > ERROR_PING:
        await db.main.add_speedtest_info(key_id, ping, download_speed, upload_speed, 1)
        error_msg = (f'{server_name}: {tool_name} – speed too slow or ping too high: '
                     f'download_speed={download_speed} or upload_speed={upload_speed} < {ERROR_SPEED} '
                     f'or ping={ping} > {ERROR_PING}')
        logger.warning(error_msg)
    else:
        await db.main.add_speedtest_info(key_id, ping, download_speed, upload_speed)

@logger.catch
async def speed_test_cli_with_fallback(key_id, server_name, localhost=0):
    """Speedtest с fallback на альтернативный метод при 403 ошибке"""
    
    # Импортируем оригинальную функцию
    from modules.speed_test import speed_test_cli
    
    # Сначала пробуем оригинальный speedtest-cli
    try:
        await speed_test_cli(key_id, server_name, localhost)
        return  # Если успешно - выходим
        
    except Exception as e:
        error_str = str(e)
        
        # Проверяем, является ли ошибка 403 блокировкой
        if any(block_phrase in error_str for block_phrase in [
            "HTTP Error 403: Forbidden", 
            "Cannot retrieve speedtest configuration",
            "Remote end closed connection without response",
            "timed out"
        ]):
            logger.warning(f"{server_name}: speedtest.net blocked/failed, trying alternative method")
            
            # Используем альтернативный метод
            await alternative_speed_test_cli(key_id, server_name, localhost)
        else:
            # Другие ошибки - записываем как ошибку
            await db.main.add_speedtest_info(key_id, 0, 0, 0, 1)
            logger.error(f"{server_name}: speedtest failed with unknown error: {error_str}")
