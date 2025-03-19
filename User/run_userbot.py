#!/usr/bin/env python3
"""
Основной файл для запуска Telegram UserBot с функциями логирования
"""
import os
import sys
import asyncio
import logging
from datetime import datetime
import importlib

# Настройка цветного вывода
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Загрузка переменных окружения
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    logger.warning("python-dotenv не установлен. Используются переменные окружения системы.")

# Получение API данных
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")

if not API_ID or not API_HASH:
    print(f"{RED}Ошибка: API_ID или API_HASH не найдены в переменных окружения{RESET}")
    print(f"{YELLOW}Создайте файл .env с вашими API данными от Telegram{RESET}")
    sys.exit(1)

# Импорт модулей
try:
    import config
    from telethon import TelegramClient, events
    from log_management import register_handlers as register_log_handlers, setup_logging
    from moderation import register_handlers as register_moderation_handlers
    from admin import register_handlers as register_admin_handlers
    from stats import register_handlers as register_stats_handlers
except ImportError as e:
    print(f"{RED}Ошибка импорта модулей: {e}{RESET}")
    print(f"{YELLOW}Убедитесь, что все необходимые модули установлены{RESET}")
    sys.exit(1)

# Попытка импорта модуля utils.commands, но не критично если его нет
try:
    from utils.commands import register_handlers as register_utils_handlers
    has_utils_commands = True
except ImportError:
    logger.warning("Модуль utils.commands не найден. Дополнительные команды не будут доступны.")
    has_utils_commands = False

async def help_handler(event):
    """Показать список доступных команд"""
    cmd_list = "📋 **Доступные команды**:\n\n"
    
    # Если есть словарь команд в конфиге, используем его
    if hasattr(config, 'COMMANDS') and isinstance(config.COMMANDS, dict):
        for cmd, desc in config.COMMANDS.items():
            cmd_list += f"**/{cmd}** - {desc}\n"
    else:
        # Иначе вывести стандартный набор команд
        cmd_list += f"**/{config.CMD_PREFIX}help** - Показать эту справку\n"
        cmd_list += f"**/{config.CMD_PREFIX}ping** - Проверить скорость ответа бота\n"
        cmd_list += f"**/{config.CMD_PREFIX}log** - Показать последние записи лога\n"
        cmd_list += f"**/{config.CMD_PREFIX}users** - Обновить кэш пользователей и админов\n"
        cmd_list += f"**/{config.CMD_PREFIX}ban** - Забанить пользователя\n"
        cmd_list += f"**/{config.CMD_PREFIX}unban** - Разбанить пользователя\n"
        cmd_list += f"**/{config.CMD_PREFIX}mute** - Заглушить пользователя\n"
        cmd_list += f"**/{config.CMD_PREFIX}unmute** - Разглушить пользователя\n"
        cmd_list += f"**/{config.CMD_PREFIX}warn** - Выдать предупреждение пользователю\n"
        cmd_list += f"**/{config.CMD_PREFIX}tmute** - Временно заглушить пользователя\n"
        cmd_list += f"**/{config.CMD_PREFIX}chatstats** - Статистика чата\n"
        cmd_list += f"**/{config.CMD_PREFIX}userstats** - Статистика пользователя\n"
    
    await event.edit(cmd_list)

async def ping_handler(event):
    """Проверка работы бота"""
    start = datetime.now()
    message = await event.edit("🏓 Pong!")
    end = datetime.now()
    ms = (end - start).microseconds / 1000
    await message.edit(f"🏓 **Pong!**\n⏱ Задержка: {ms:.2f} мс")

async def main():
    """Основная функция"""
    try:
        # Настройка логирования
        setup_logging()
        
        # Создание и запуск клиента
        client = TelegramClient(
            config.SESSION_NAME,
            API_ID,
            API_HASH,
            device_model="Termux UserBot",
            system_version="1.0",
            app_version="1.0"
        )
        
        print(f"{BLUE}Подключение к Telegram...{RESET}")
        await client.start()
        
        # Регистрация базовых обработчиков
        client.add_event_handler(
            help_handler,
            events.NewMessage(pattern=f"\\{config.CMD_PREFIX}help")
        )
        
        client.add_event_handler(
            ping_handler,
            events.NewMessage(pattern=f"\\{config.CMD_PREFIX}ping")
        )
        
        # Регистрация обработчиков из других модулей
        register_log_handlers(client)
        register_moderation_handlers(client)
        register_admin_handlers(client)
        register_stats_handlers(client)
        
        # Регистрация утилитных обработчиков, если модуль доступен
        if has_utils_commands:
            register_utils_handlers(client)
        
        # Получаем информацию о пользователе
        me = await client.get_me()
        print(f"{GREEN}UserBot запущен!{RESET}")
        print(f"{BLUE}Аккаунт: {me.first_name} (@{me.username}){RESET}")
        logger.info(f"UserBot started as {me.first_name} (@{me.username})")
        
        # Держим бота запущенным до отключения
        print(f"{YELLOW}Нажмите Ctrl+C для остановки...{RESET}")
        await client.run_until_disconnected()
        
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Работа прервана пользователем{RESET}")
    except Exception as e:
        print(f"{RED}Ошибка: {str(e)}{RESET}")
        logger.error(f"Критическая ошибка: {e}")

if __name__ == "__main__":
    # Запускаем основную функцию
    asyncio.run(main())