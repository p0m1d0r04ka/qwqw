#!/usr/bin/env python3
"""
Основной модуль Telegram UserBot
Предназначен для запуска только в среде Termux на Android
"""
import os
import sys
import logging
import asyncio
import platform
from datetime import datetime

from telethon import TelegramClient, events
from telethon.tl.types import User
from dotenv import load_dotenv

# Проверка запуска в Termux
def check_termux_environment():
    """Проверяет, что скрипт запущен в среде Termux"""
    # Проверка наличия характерных для Termux файлов и переменных
    termux_signs = [
        os.path.exists('/data/data/com.termux'),
        os.getenv('TERMUX_VERSION') is not None,
        'Android' in platform.version()
    ]
    # Если тестовый режим включен, пропускаем проверку
    if os.getenv('USERBOT_TEST_MODE'):
        return True
    # Если ни один из признаков Termux не найден
    if not any(termux_signs):
        print("\033[91mОшибка: Этот UserBot предназначен только для запуска в Termux!\033[0m")
        print("\033[93mПожалуйста, установите Termux из F-Droid и запустите скрипт в нем:\033[0m")
        print("\033[93mhttps://f-droid.org/packages/com.termux/\033[0m")
        print("\033[93mИнструкции по установке: см. README.md\033[0m")
        return False
    return True

# Загружаем переменные окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Получаем данные API из переменных окружения
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")

# Проверяем наличие API данных
if not API_ID or not API_HASH:
    logger.error("API_ID или API_HASH не найдены в переменных окружения!")
    sys.exit(1)

# Создаем клиент с нашими данными
client = TelegramClient(
    'userbot',  # Имя файла сессии
    API_ID,
    API_HASH,
    device_model="Termux UserBot",
    system_version="1.0",
    app_version="1.0"
)

# Словарь для хранения предупреждений пользователей
warnings = {}

# Словарь для хранения кэша админов
admin_cache = {}

async def is_admin(chat_id: int, user_id: int) -> bool:
    """Проверка на администратора"""
    if chat_id not in admin_cache:
        admin_cache[chat_id] = {}
        async for admin in client.iter_participants(chat_id, filter=lambda x: x.admin_rights):
            admin_cache[chat_id][admin.id] = True
    return user_id in admin_cache[chat_id]

@client.on(events.NewMessage(pattern='/help'))
async def help_handler(event):
    """Показать список доступных команд"""
    sender = await event.get_sender()
    if not isinstance(sender, User):
        return
    
    help_text = """📋 **Доступные команды:**

🔹 **Основные команды:**
• `/help` - Показать это сообщение
• `/ping` - Проверить работу бота
• `/log` - Просмотр логов работы бота
• `/users` - Обновить список пользователей чата

🔸 **Команды модерации:**
• `/ban` - Забанить пользователя
• `/unban` - Разбанить пользователя
• `/warn` - Выдать предупреждение
• `/unwarn` - Снять предупреждение
• `/mute` - Заглушить пользователя
• `/unmute` - Снять заглушение
• `/tmute <минуты>` - Временное заглушение

📊 **Статистика:**
• `/chatstats` - Статистика чата
• `/userstats` - Статистика пользователя

🔧 **Дополнительно:**
• `/mention_all` - Упомянуть всех участников"""

    try:
        await event.reply(help_text)
        logger.info(f"Команда help выполнена для пользователя {sender.id}")
    except Exception as e:
        logger.error(f"Ошибка при выполнении команды help: {e}")

@client.on(events.NewMessage(pattern='/ping'))
async def ping_handler(event):
    """Проверка работы бота"""
    try:
        start = datetime.now()
        message = await event.reply('Pong!')
        end = datetime.now()
        ms = (end - start).microseconds / 1000
        await message.edit(f'Pong! `{ms}ms`')
        logger.info(f"Команда ping выполнена. Время отклика: {ms}ms")
    except Exception as e:
        logger.error(f"Ошибка при выполнении команды ping: {e}")

async def main():
    """Основная функция"""
    # Импортируем модули с командами
    import log_management
    import moderation
    import admin
    import stats
    from utils.commands import register_handlers as utils_register_handlers
    
    # Регистрируем обработчики команд
    log_management.register_handlers(client)
    moderation.register_handlers(client)
    admin.register_handlers(client)
    stats.register_handlers(client)
    utils_register_handlers(client)
    
    try:
        logger.info("Запуск UserBot...")
        print("UserBot запущен! Нажмите Ctrl+C для выхода.")
        
        # Запускаем клиент
        await client.start()
        
        # Получаем информацию о боте
        me = await client.get_me()
        logger.info(f"UserBot запущен как {me.first_name} (@{me.username})")
        
        # Держим бота запущенным
        await client.run_until_disconnected()
        
    except KeyboardInterrupt:
        logger.info("Получен сигнал завершения работы")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
    finally:
        # Закрываем соединение
        await client.disconnect()
        logger.info("UserBot остановлен")

if __name__ == "__main__":
    # Проверяем запуск в Termux перед всеми операциями
    if not check_termux_environment():
        print("\n\033[91mЗапуск прерван: UserBot работает только в Termux!\033[0m")
        sys.exit(1)
        
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nРабота прервана пользователем")
    except Exception as e:
        print(f"\nКритическая ошибка: {e}")