#!/usr/bin/env python3
"""
Тестовый скрипт для проверки интеграции альтернативного speedtest
"""

import asyncio
import sys
import os

# Добавляем путь к модулям
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_alternative_speedtest():
    """Тест альтернативной функции speedtest"""
    
    try:
        from modules.speedtest_integration import alternative_speed_test_cli
        
        print("=== Тестируем альтернативный speedtest ===")
        print("Тестируем localhost (должен использовать ookla-speedtest)...")
        
        # Тест localhost (будет ошибка без ookla-speedtest, но проверим логику)
        await alternative_speed_test_cli(999, "test-localhost", localhost=1)
        
        print("\nТестируем VPN режим (должен использовать curl)...")
        
        # Тест VPN режима (будет ошибка без ss-local, но проверим логику)
        await alternative_speed_test_cli(998, "test-vpn", localhost=0)
        
        print("\n=== Тест завершен ===")
        
    except ImportError as e:
        print(f"Ошибка импорта: {e}")
        print("Проверьте, что все модули на месте")
    except Exception as e:
        print(f"Ошибка теста: {e}")

if __name__ == "__main__":
    asyncio.run(test_alternative_speedtest())
