#!/usr/bin/env python3
"""
Основной скрипт для запуска Telegram UserBot без веб-интерфейса
"""

import os
import sys
import asyncio
import logging
import argparse
from datetime import datetime

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ANSI цвета для вывода в консоль
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'

def setup_environment():
    """Настройка переменных окружения и проверка зависимостей"""
    print(f"{YELLOW}Подготовка окружения...{RESET}")
    
    # Проверка наличия .env файла
    if not os.path.exists(".env") and not os.path.exists("attached_assets/.env"):
        print(f"{RED}Файл .env не найден!{RESET}")
        create_env = input("Создать файл .env? (y/n): ")
        
        if create_env.lower() == 'y':
            api_id = input("Введите API_ID: ")
            api_hash = input("Введите API_HASH: ")
            
            with open(".env", "w") as f:
                f.write(f"API_ID={api_id}\n")
                f.write(f"API_HASH={api_hash}\n")
            
            print(f"{GREEN}Файл .env создан{RESET}")
        else:
            print(f"{RED}Невозможно продолжить без файла .env{RESET}")
            return False
    
    # Проверка зависимостей
    try:
        from telethon import TelegramClient
        print(f"{GREEN}Зависимости установлены{RESET}")
    except ImportError:
        print(f"{RED}Библиотека telethon не установлена!{RESET}")
        install = input("Установить необходимые библиотеки? (y/n): ")
        
        if install.lower() == 'y':
            import subprocess
            print(f"{YELLOW}Установка зависимостей...{RESET}")
            subprocess.call([sys.executable, "-m", "pip", "install", "telethon", "python-dotenv", "cryptg"])
            print(f"{GREEN}Зависимости установлены{RESET}")
        else:
            print(f"{RED}Невозможно продолжить без установки зависимостей{RESET}")
            return False
    
    return True

async def main():
    """Основная функция запуска"""
    # Проверка окружения
    if not setup_environment():
        return
    
    print(f"\n{GREEN}{BOLD}=== Telegram UserBot ==={RESET}")
    
    # Обработка аргументов командной строки
    parser = argparse.ArgumentParser(description='Запуск Telegram UserBot без веб-интерфейса')
    parser.add_argument('--debug', action='store_true', help='Включить режим отладки')
    parser.add_argument('--termux', action='store_true', help='Оптимизация для Termux')
    args = parser.parse_args()
    
    # Настройка уровня логирования
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Режим отладки включен")
    
    # Оптимизации для Termux
    if args.termux or os.path.exists("/data/data/com.termux"):
        logger.info("Применены оптимизации для Termux")
        os.environ["PYTHONOPTIMIZE"] = "1"
    
    # Импорт основного модуля UserBot
    try:
        import userbot
    except ImportError:
        print(f"{RED}Ошибка импорта модуля userbot{RESET}")
        print(f"{YELLOW}Убедитесь, что файл userbot.py находится в текущем каталоге{RESET}")
        return
    
    # Запуск UserBot
    print(f"{BLUE}Запуск UserBot... {datetime.now().strftime('%H:%M:%S')}{RESET}")
    print(f"{YELLOW}Нажмите Ctrl+C для завершения{RESET}")
    print(f"{GREEN}{'='*40}{RESET}")
    
    try:
        await userbot.main()
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Работа прервана пользователем{RESET}")
    except Exception as e:
        print(f"\n{RED}Произошла ошибка: {e}{RESET}")
        logger.error(f"Runtime error: {e}")
    finally:
        print(f"{BLUE}UserBot остановлен. {datetime.now().strftime('%H:%M:%S')}{RESET}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Работа прервана пользователем{RESET}")
    except Exception as e:
        print(f"\n{RED}Критическая ошибка: {e}{RESET}")