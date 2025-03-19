#!/data/data/com.termux/files/usr/bin/bash

# Цвета для вывода
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}┌───────────────────────────────────────┐${NC}"
echo -e "${BLUE}│  Установка Telegram UserBot в Termux  │${NC}"
echo -e "${BLUE}└───────────────────────────────────────┘${NC}"

# Проверка работы в Termux
if [ ! -d "/data/data/com.termux" ]; then
    echo -e "${RED}Ошибка: Скрипт должен быть запущен в Termux!${NC}"
    exit 1
fi

# Обновление репозиториев
echo -e "${YELLOW}Обновление репозиториев Termux...${NC}"
pkg update -y

# Установка необходимых пакетов
echo -e "${YELLOW}Установка необходимых пакетов...${NC}"
pkg install -y python git

# Установка pip и обновление
echo -e "${YELLOW}Установка и обновление pip...${NC}"
pkg install -y python-pip
pip install --upgrade pip

# Установка необходимых Python-библиотек
echo -e "${YELLOW}Установка Python-библиотек...${NC}"
pip install telethon python-dotenv cryptg

# Создание каталогов
echo -e "${YELLOW}Создание структуры каталогов...${NC}"
mkdir -p $HOME/userbot
mkdir -p $HOME/userbot/utils

# Скачивание основных файлов
echo -e "${YELLOW}Скачивание файлов UserBot...${NC}"
cd $HOME/userbot

# Создание базовой структуры директорий
mkdir -p $HOME/userbot/utils
mkdir -p $HOME/userbot/plugins

# Загрузка файлов проекта
# Опция 1: Через Git
if command -v git &> /dev/null; then
    echo -e "${BLUE}Обнаружен Git, клонирование репозитория...${NC}"
    # При необходимости заменить URL репозитория
    REPO_URL="https://github.com/username/telegram-userbot.git"
    # Клонировать во временную директорию
    TEMP_DIR=$(mktemp -d)
    git clone "$REPO_URL" "$TEMP_DIR" || {
        echo -e "${RED}Ошибка при клонировании репозитория!${NC}"
        echo -e "${YELLOW}Продолжение установки через загрузку отдельных файлов...${NC}"
    }
    
    # Если клонирование успешно, копируем файлы
    if [ -d "$TEMP_DIR/.git" ]; then
        cp -r "$TEMP_DIR"/* "$HOME/userbot/"
        rm -rf "$TEMP_DIR"
        echo -e "${GREEN}Репозиторий успешно клонирован!${NC}"
    fi
else
    echo -e "${YELLOW}Git не установлен, загрузка отдельных файлов...${NC}"
fi

# Опция 2: Через скачивание отдельных файлов (если Git не сработал)
if [ ! -f "$HOME/userbot/userbot.py" ]; then
    echo -e "${YELLOW}Загрузка основных файлов UserBot...${NC}"
    
    # Создаем базовые файлы
    # userbot.py
    cat > $HOME/userbot/userbot.py << 'EOF'
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
    # Эти импорты будут доступны при полной установке
    try:
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
    except ImportError as e:
        logger.warning(f"Некоторые модули не найдены: {e}")
        logger.info("Базовая функциональность будет работать без дополнительных модулей")
    
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
EOF

    # Создание log_management_main.py
    cat > $HOME/userbot/log_management_main.py << 'EOF'
#!/usr/bin/env python3
"""
Основной файл для запуска Telegram UserBot с функциями логирования
"""
import os
import sys
import logging
import asyncio
import platform

# Проверка среды выполнения
def check_termux_environment():
    """Проверяет, что скрипт запущен в среде Termux"""
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
        return False
    return True

if __name__ == "__main__":
    if not check_termux_environment():
        sys.exit(1)

from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("userbot.log", mode='a'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Базовые обработчики команд для автономной работы
async def help_handler(event):
    """Показать список доступных команд"""
    help_text = """📋 **Доступные команды:**

🔹 **Основные команды:**
• `/help` - Показать это сообщение
• `/ping` - Проверить работу бота

⚠️ Дополнительные команды будут доступны после завершения установки."""
    await event.reply(help_text)

async def ping_handler(event):
    """Проверка работы бота"""
    message = await event.reply('Pong!')
    await message.edit('Pong! UserBot работает!')

async def main():
    """Основная функция"""
    from telethon import TelegramClient, events
    
    # Получаем данные API из переменных окружения
    API_ID = os.getenv("API_ID")
    API_HASH = os.getenv("API_HASH")
    
    # Проверяем наличие API данных
    if not API_ID or not API_HASH:
        logger.error("API_ID или API_HASH не найдены в переменных окружения!")
        print("\033[91mОшибка: API_ID или API_HASH не найдены!\033[0m")
        print("\033[93mПожалуйста, отредактируйте файл .env и укажите правильные значения.\033[0m")
        sys.exit(1)
    
    # Создаем клиент
    client = TelegramClient(
        'userbot',
        API_ID,
        API_HASH,
        device_model="Termux UserBot",
        system_version="1.0",
        app_version="1.0"
    )
    
    # Регистрируем базовые обработчики
    client.add_event_handler(
        help_handler,
        events.NewMessage(pattern='/help')
    )
    
    client.add_event_handler(
        ping_handler,
        events.NewMessage(pattern='/ping')
    )
    
    try:
        print("\033[92mЗапуск UserBot...\033[0m")
        
        # Запускаем клиент
        await client.start()
        
        # Получаем информацию о боте
        me = await client.get_me()
        print(f"\033[92mUserBot запущен как {me.first_name} (@{me.username})\033[0m")
        print("\033[93mНажмите Ctrl+C для выхода\033[0m")
        
        # Держим бота запущенным
        await client.run_until_disconnected()
        
    except KeyboardInterrupt:
        print("\n\033[93mРабота прервана пользователем\033[0m")
    except Exception as e:
        print(f"\n\033[91mКритическая ошибка: {e}\033[0m")
    finally:
        # Закрываем соединение
        await client.disconnect()
        print("\033[93mUserBot остановлен\033[0m")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\033[93mРабота прервана пользователем\033[0m")
    except Exception as e:
        print(f"\n\033[91mКритическая ошибка: {e}\033[0m")
EOF

    # Создание utils/__init__.py
    cat > $HOME/userbot/utils/__init__.py << 'EOF'
# Пакет с утилитами для Telegram UserBot
EOF

    # Создание utils/commands.py
    cat > $HOME/userbot/utils/commands.py << 'EOF'
#!/usr/bin/env python3
"""Модуль с общими командами для Telegram UserBot"""

from telethon import TelegramClient, events
from telethon.tl.types import ChannelParticipantsAdmins

def register_handlers(client: TelegramClient):
    """Register utility command handlers"""
    
    @client.on(events.NewMessage(pattern='/mention_all'))
    async def mention_all(event):
        """Command to mention all users in chat"""
        # Проверяем, что команда отправлена в групповом чате
        if event.is_private:
            await event.reply("Эта команда доступна только в групповых чатах!")
            return
            
        # Получаем информацию об отправителе
        sender = await event.get_sender()
        sender_id = sender.id
        
        # Получаем информацию о чате
        chat = await event.get_chat()
        chat_id = event.chat_id
        
        # Проверяем, является ли отправитель администратором
        is_admin = False
        async for admin in client.iter_participants(chat_id, filter=ChannelParticipantsAdmins):
            if admin.id == sender_id:
                is_admin = True
                break
                
        if not is_admin:
            await event.reply("Только администраторы могут использовать эту команду!")
            return
            
        # Собираем всех участников чата
        participants = []
        async for participant in client.iter_participants(chat_id):
            if not participant.bot and participant.id != sender_id:
                participants.append(participant)
                
        # Формируем сообщение с упоминаниями
        chunks = []
        chunk = ""
        for participant in participants:
            mention = f"[{participant.first_name}](tg://user?id={participant.id})"
            if len(chunk) + len(mention) + 2 > 4000:  # Ограничение Telegram на длину сообщения
                chunks.append(chunk)
                chunk = ""
            chunk += mention + ", "
            
        if chunk:
            chunks.append(chunk)
            
        # Отправляем сообщения с упоминаниями
        for chunk in chunks:
            await event.reply(f"Внимание! {chunk[:-2]}")
EOF

    echo -e "${GREEN}Основные файлы созданы успешно!${NC}"
fi

# Создание файла .env для хранения API данных
if [ ! -f "$HOME/userbot/.env" ]; then
    echo -e "${YELLOW}Создание конфигурационного файла .env...${NC}"
    echo "# Telegram API данные" > .env
    echo "API_ID=ваш_api_id" >> .env
    echo "API_HASH=ваш_api_hash" >> .env
    echo -e "${GREEN}Файл .env создан. Необходимо указать ваши данные API.${NC}"
fi

# Создание файла запуска
echo -e "${YELLOW}Создание скрипта запуска...${NC}"
cat > $HOME/userbot/start_userbot.sh << 'EOF'
#!/data/data/com.termux/files/usr/bin/bash
# Скрипт запуска Telegram UserBot в Termux

# Цвета для вывода
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Проверка запуска в Termux
if [ ! -d "/data/data/com.termux" ]; then
    echo -e "${RED}Ошибка: Скрипт должен быть запущен в Termux!${NC}"
    echo -e "${YELLOW}Установите Termux из F-Droid:${NC}"
    echo -e "${BLUE}https://f-droid.org/packages/com.termux/${NC}"
    exit 1
fi

# Проверка наличия файлов
if [ ! -f "$HOME/userbot/log_management_main.py" ]; then
    echo -e "${RED}Ошибка: Файл log_management_main.py не найден!${NC}"
    echo -e "${YELLOW}Запустите скрипт установки заново.${NC}"
    exit 1
fi

# Переход в директорию userbot
cd $HOME/userbot

# Запуск UserBot
echo -e "${GREEN}Запуск Telegram UserBot...${NC}"
python log_management_main.py
EOF

# Делаем скрипт запуска исполняемым
chmod +x $HOME/userbot/start_userbot.sh

echo -e "${GREEN}┌─────────────────────────────────────────────┐${NC}"
echo -e "${GREEN}│  Установка UserBot успешно завершена!       │${NC}"
echo -e "${GREEN}└─────────────────────────────────────────────┘${NC}"
echo -e ""
echo -e "${YELLOW}Для завершения установки необходимо:${NC}"
echo -e "1. Отредактировать файл ${BLUE}$HOME/userbot/.env${NC} и указать API_ID и API_HASH"
echo -e "2. Запустить UserBot командой: ${BLUE}$HOME/userbot/start_userbot.sh${NC}"
echo -e ""
echo -e "${YELLOW}При первом запуске потребуется ввести номер телефона и код подтверждения${NC}"