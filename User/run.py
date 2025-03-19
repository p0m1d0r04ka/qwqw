#!/usr/bin/env python3
import os
import sys
import logging
import asyncio
from datetime import datetime
from dotenv import load_dotenv

# Настройка цветного вывода
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'

# Загрузка переменных окружения
load_dotenv()

# Проверка API данных
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")

if not API_ID or not API_HASH:
    print(f"{RED}Ошибка: API_ID или API_HASH не найдены в .env файле{RESET}")
    print(f"{YELLOW}Убедитесь, что файл .env создан и содержит необходимые данные{RESET}")
    sys.exit(1)

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def main():
    """Основная функция"""
    try:
        from telethon import TelegramClient
        
        # Создание клиента
        client = TelegramClient(
            'userbot',
            API_ID,
            API_HASH,
            device_model="Termux UserBot",
            system_version="1.0",
            app_version="1.0"
        )
        
        print(f"{BLUE}Подключение к Telegram...{RESET}")
        await client.start()
        
        # Получаем информацию о пользователе
        me = await client.get_me()
        print(f"{GREEN}UserBot запущен!{RESET}")
        print(f"{BLUE}Аккаунт: {me.first_name} (@{me.username}){RESET}")
        
        # Держим бота запущенным
        await client.run_until_disconnected()
        
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Работа прервана пользователем{RESET}")
    except Exception as e:
        print(f"{RED}Ошибка: {str(e)}{RESET}")
        logger.error(f"Критическая ошибка: {e}")

if __name__ == "__main__":
    # Запускаем основную функцию
    asyncio.run(main())