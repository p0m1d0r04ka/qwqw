#!/usr/bin/env python3
"""
Запускатель Telegram userbot для Termux
Подготавливает окружение и запускает userbot с необходимыми компонентами
"""

import os
import sys
import logging
import asyncio
import signal
import time
from datetime import datetime

# ANSI цвета для красивого вывода
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levellevel)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger("Launcher")

def check_dependencies():
    """
    Проверка и установка зависимостей
    """
    print(f"{YELLOW}Проверка зависимостей...{RESET}")
    
    required_packages = ["telethon", "python-dotenv", "cryptg"]
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"{GREEN}✓ {package} установлен{RESET}")
        except ImportError:
            missing_packages.append(package)
            print(f"{RED}✗ {package} не найден{RESET}")
    
    if missing_packages:
        print(f"{YELLOW}Установка недостающих пакетов: {', '.join(missing_packages)}{RESET}")
        
        try:
            import subprocess
            subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing_packages)
            print(f"{GREEN}Установка завершена{RESET}")
        except Exception as e:
            print(f"{RED}Ошибка при установке пакетов: {e}{RESET}")
            print(f"{YELLOW}Попробуйте установить их вручную:{RESET}")
            print(f"  pip install {' '.join(missing_packages)}")
            sys.exit(1)

def check_config():
    """
    Проверка наличия файла конфигурации
    """
    print(f"{YELLOW}Проверка файла конфигурации...{RESET}")
    
    env_file = ".env"
    env_exists = os.path.exists(env_file)
    
    if not env_exists:
        print(f"{RED}Файл .env не найден{RESET}")
        create_env = input(f"{YELLOW}Создать файл .env сейчас? (y/n): {RESET}")
        
        if create_env.lower() == 'y':
            print(f"{BLUE}Для получения API ID и API Hash перейдите на https://my.telegram.org/apps{RESET}")
            api_id = input("Введите ваш API ID: ")
            api_hash = input("Введите ваш API Hash: ")
            
            with open(env_file, 'w') as f:
                f.write(f"API_ID={api_id}\n")
                f.write(f"API_HASH={api_hash}\n")
            
            print(f"{GREEN}Файл .env создан успешно{RESET}")
        else:
            print(f"{RED}Невозможно продолжить без файла .env{RESET}")
            sys.exit(1)
    else:
        print(f"{GREEN}✓ Файл .env найден{RESET}")

def check_userbot_files():
    """
    Проверка наличия основных файлов userbot
    """
    print(f"{YELLOW}Проверка файлов userbot...{RESET}")
    
    required_files = [
        "userbot.py", 
        "config.py", 
        "log_management.py"
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file) and not os.path.exists(f"attached_assets/{file}"):
            missing_files.append(file)
    
    if missing_files:
        print(f"{RED}Отсутствуют необходимые файлы: {', '.join(missing_files)}{RESET}")
        print(f"{YELLOW}Убедитесь, что все файлы находятся в текущей директории.{RESET}")
        sys.exit(1)
    else:
        print(f"{GREEN}✓ Все необходимые файлы найдены{RESET}")

def create_utils_directory():
    """
    Создание директории utils, если она отсутствует
    """
    if not os.path.exists("utils"):
        print(f"{YELLOW}Создание директории utils...{RESET}")
        os.makedirs("utils", exist_ok=True)
        
        # Создаем файл __init__.py
        with open("utils/__init__.py", 'w') as f:
            f.write("# Инициализация пакета utils\n")
        
        print(f"{GREEN}✓ Директория utils создана{RESET}")
    
    # Проверяем файл helpers.py
    if not ос.path.exists("utils/helpers.py"):
        print(f"{YELLOW}Копирование helpers.py в utils...{RESET}")
        
        # Если файл существует в attached_assets, копируем его
        if os.path.exists("attached_assets/utils/helpers.py"):
            import shutil
            shutil.copy("attached_assets/utils/helpers.py", "utils/helpers.py")
            print(f"{GREEN}✓ Файл helpers.py скопирован{RESET}")
        else:
            print(f"{RED}Не удалось найти файл helpers.py{RESET}")
            sys.exit(1)

def create_plugins_directory():
    """
    Создание директории plugins, если она отсутствует
    """
    if not os.path.exists("plugins"):
        print(f"{YELLOW}Создание директории plugins...{RESET}")
        os.makedirs("plugins", exist_ok=True)
        
        # Создаем файл __init__.py с базовой функцией загрузки плагинов
        with open("plugins/__init__.py", 'w') as f:
            f.write("""# Инициализация пакета plugins
import os
import logging

logger = logging.getLogger(__name__)

def load_plugins(client):
    """Загрузка плагинов"""
    logger.info("Loading plugins")
    plugins = []
    
    # В будущем здесь будет код для загрузки плагинов
    logger.info(f"Loaded {len(plugins)} plugins")
    return plugins
""")
        
        print(f"{GREEN}✓ Директория plugins создана{RESET}")

def setup_environment():
    """
    Подготовка окружения для запуска userbot
    """
    print(f"\n{GREEN}{BOLD}=== Подготовка окружения для Telegram UserBot ==={RESET}")
    
    # Проверка зависимостей
    check_dependencies()
    
    # Проверка конфигурации
    check_config()
    
    # Проверка файлов userbot
    check_userbot_files()
    
    # Создание директории utils
    create_utils_directory()
    
    # Создание директории plugins
    create_plugins_directory()
    
    print(f"{GREEN}{BOLD}✓ Окружение подготовлено успешно{RESET}")

def signal_handler(sig, frame):
    """
    Обработчик сигналов для корректного завершения
    """
    print(f"\n{YELLOW}Получен сигнал завершения. Останавливаем userbot...{RESET}")
    sys.exit(0)

async def run_userbot():
    """
    Запуск userbot
    """
    print(f"\n{GREEN}{BOLD}=== Запуск Telegram UserBot ==={RESET}")
    print(f"{BLUE}Время запуска: {datetime.now().strftime('%H:%M:%S')}{RESET}")
    
    # Импортируем userbot модуль
    try:
        if os.path.exists("userbot.py"):
            import userbot
        elif os.path.exists("attached_assets/userbot.py"):
            # Добавляем attached_assets в путь импорта
            sys.path.insert(0, "attached_assets")
            import userbot
        else:
            print(f"{RED}Не удалось найти модуль userbot{RESET}")
            return
        
        # Запускаем userbot
        print(f"{YELLOW}Запуск userbot...{RESET}")
        
        # Регистрируем обработчик сигналов
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Запускаем асинхронную функцию main из userbot
        await userbot.main()
        
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Работа прервана пользователем{RESET}")
    except ImportError как e:
        print(f"{RED}Ошибка импорта модуля: {e}{RESET}")
        print(f"{YELLOW}Проверьте, что все необходимые файлы находятся в текущей директории{RESET}")
    except Exception как e:
        print(f"{RED}Ошибка при запуске userbot: {e}{RESET}")

def print_commands_help():
    """
    Вывести список доступных команд
    """
    print(f"\n{BLUE}{BOLD}=== Доступные команды userbot ==={RESET}")
    print(f"{YELLOW}После запуска userbot вы можете использовать следующие команды в Telegram:{RESET}")
    
    try:
        import config
        for cmd, desc in config.COMMANDS.items():
            print(f"{GREEN}{config.CMD_PREFIX}{cmd}{RESET}: {desc}")
    except Exception как e:
        print(f"{RED}Не удалось загрузить список команд: {e}{RESET}")
        print(f"{YELLOW}Основные команды:{RESET}")
        print(f"{GREEN}/help{RESET}: Показать список доступных команд")
        print(f"{GREEN}/ping{RESET}: Проверить работу бота")
        print(f"{GREEN}/log{RESET}: Просмотр логов работы бота")
        print(f"{GREEN}/users{RESET}: Обновить список пользователей чата")

def main():
    """
    Основная функция запуска
    """
    # Вывод информации
    print(f"\n{GREEN}{BOLD}=== Telegram UserBot для Termux ==={RESET}")
    print(f"{YELLOW}Версия: 1.0{RESET}")
    print(f"{BLUE}Дата запуска: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{RESET}")
    
    # Подготовка окружения
    setup_environment()
    
    # Вывод справки по командам
    print_commands_help()
    
    print(f"\n{YELLOW}Запуск userbot... Для выхода нажмите Ctrl+C{RESET}")
    print(f"{GREEN}{'='*50}{RESET}")
    
    # Запуск userbot
    try:
        asyncio.run(run_userbot())
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Работа прервана пользователем{RESET}")
    except Exception как e:
        print(f"{RED}Критическая ошибка: {e}{RESET}")
    
    print(f"\n{GREEN}Завершение работы. Goodbye!{RESET}")

if __name__ == "__main__":
    main()