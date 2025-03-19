#!/usr/bin/env python3
"""
Простой скрипт запуска Telegram UserBot для Termux
Минимальная версия без дополнительных проверок
"""
import os
import sys
import asyncio
import logging
from datetime import datetime
from dotenv import load_dotenv

# Настройка цветного вывода
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("userbot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def print_banner():
    """Вывод информации о запуске"""
    print(f"{BLUE}┌───────────────────────────────────────┐{RESET}")
    print(f"{BLUE}│  Telegram UserBot - Простой запуск    │{RESET}")
    print(f"{BLUE}└───────────────────────────────────────┘{RESET}")
    print()

async def main():
    """Основная функция запуска"""
    print_banner()
    
    # Загрузка переменных окружения
    load_dotenv()
    
    # Проверка API данных
    API_ID = os.getenv("API_ID")
    API_HASH = os.getenv("API_HASH")
    
    if not API_ID or not API_HASH:
        print(f"{RED}Ошибка: API_ID или API_HASH не найдены в .env файле{RESET}")
        print(f"{YELLOW}Создайте файл .env с вашими API данными:{RESET}")
        print("API_ID=your_api_id")
        print("API_HASH=your_api_hash")
        return
    
    # Импортируем telethon здесь, чтобы показать понятную ошибку при отсутствии
    try:
        from telethon import TelegramClient, events
    except ImportError:
        print(f"{RED}Ошибка: библиотека telethon не установлена{RESET}")
        print(f"{YELLOW}Установите необходимые библиотеки:{RESET}")
        print("pip install telethon python-dotenv cryptg")
        return
    
    # Создание клиента
    client = TelegramClient(
        'userbot',
        API_ID,
        API_HASH,
        device_model="Termux UserBot",
        system_version="1.0",
        app_version="1.0"
    )
    
    # Регистрация базовых обработчиков
    
    @client.on(events.NewMessage(pattern=r'/help'))
    async def help_command(event):
        """Показать список доступных команд"""
        commands = {
            "/help": "Показать это сообщение",
            "/ping": "Проверить время отклика бота"
        }
        
        message = "📋 **Доступные команды**:\n\n"
        for cmd, desc in commands.items():
            message += f"**{cmd}** - {desc}\n"
        
        await event.reply(message)
    
    @client.on(events.NewMessage(pattern=r'/ping'))
    async def ping_command(event):
        """Проверка работы бота"""
        start = datetime.now()
        message = await event.reply("🏓 Pong!")
        end = datetime.now()
        ms = (end - start).microseconds / 1000
        await message.edit(f"🏓 **Pong!**\n⏱ Задержка: {ms:.2f} мс")
    
    # Запуск клиента
    try:
        print(f"{YELLOW}Подключение к Telegram...{RESET}")
        await client.start()
        
        # Получаем информацию о пользователе
        me = await client.get_me()
        print(f"{GREEN}UserBot запущен!{RESET}")
        print(f"{BLUE}Аккаунт: {me.first_name} (@{me.username}){RESET}")
        logger.info(f"UserBot запущен как {me.first_name} (@{me.username})")
        
        # Держим бота запущенным
        print(f"{YELLOW}Нажмите Ctrl+C для остановки...{RESET}")
        await client.run_until_disconnected()
        
    except Exception as e:
        print(f"{RED}Ошибка: {str(e)}{RESET}")
        logger.error(f"Критическая ошибка: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Работа прервана пользователем{RESET}")
    except Exception as e:
        print(f"{RED}Необработанная ошибка: {str(e)}{RESET}")
        logger.error(f"Необработанная ошибка: {e}")