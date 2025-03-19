#!/usr/bin/env python3
#!/usr/bin/env python3
"""
Консольный запуск Telegram UserBot без веб-интерфейса
Простой скрипт для запуска напрямую в терминале или Termux
"""

import os
import sys
import asyncio
import logging
import argparse
from datetime import datetime

# Устанавливаем режим консоли
os.environ['CONSOLE_MODE'] = '1'

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ANSI цвета для терминала
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'

def check_requirements():
    """Проверка наличия необходимых зависимостей"""
    requirements = ['telethon', 'python-dotenv']
    missing = []
    
    for req in requirements:
        try:
            if req == 'python-dotenv':
                __import__('dotenv')
            else:
                __import__(req)
                
        except ImportError:
            missing.append(req)
    
    if missing:
        print(f"{YELLOW}Отсутствуют необходимые библиотеки: {', '.join(missing)}{RESET}")
        install = input("Установить сейчас? (y/n): ")
        
        if install.lower() == 'y':
            import subprocess
            print(f"{BLUE}Установка библиотек...{RESET}")
            subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing)
            print(f"{GREEN}Библиотеки установлены{RESET}")
        else:
            print(f"{RED}Невозможно продолжить без необходимых библиотек{RESET}")
            sys.exit(1)

def check_config():
    """Проверка наличия конфигурационных файлов"""
    env_file = '.env'
    session_files = ['userbot.session', 'sessions/userbot.session']
    
    # Проверка .env файла
    if not os.path.exists(env_file):
        print(f"{YELLOW}Файл .env не найден{RESET}")
        create = input("Создать файл .env? (y/n): ")
        
        if create.lower() == 'y':
            api_id = input("Введите API_ID: ")
            api_hash = input("Введите API_HASH: ")
            
            with open(env_file, 'w') as f:
                f.write(f"API_ID={api_id}\n")
                f.write(f"API_HASH={api_hash}\n")
                
            print(f"{GREEN}Файл .env создан{RESET}")
        else:
            print(f"{RED}Невозможно продолжить без файла .env{RESET}")
            sys.exit(1)
    
    # Проверка файла сессии
    session_exists = any(os.path.exists(f) for f in session_files)
    if not session_exists:
        print(f"{YELLOW}Файл сессии не найден.{RESET}")
        print(f"{BLUE}Вам будет предложено войти в аккаунт Telegram при запуске.{RESET}")
    
    return True

async def main():
    """Основная функция запуска"""
    print(f"\n{GREEN}{BOLD}=== Telegram UserBot (Консольная версия) ==={RESET}")
    print(f"{BLUE}Запуск в консольном режиме{RESET}")
    print(f"{YELLOW}Время запуска: {datetime.now().strftime('%H:%M:%S')}{RESET}")
    
    # Обработка аргументов командной строки
    parser = argparse.ArgumentParser(description='Запуск Telegram UserBot')
    parser.add_argument('--debug', action='store_true', help='Включить отладочный режим')
    parser.add_argument('--termux', action='store_true', help='Оптимизации для Termux')
    args = parser.parse_args()
    
    # Настройка уровня логирования
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        print(f"{YELLOW}Режим отладки включен{RESET}")
    
    # Проверка и настройка окружения
    check_requirements()
    check_config()
    
    # Оптимизации для Termux
    if args.termux or os.path.exists('/data/data/com.termux'):
        print(f"{BLUE}Применены оптимизации для Termux{RESET}")
        os.environ['PYTHONOPTIMIZE'] = '1'
    
    # Импорт и запуск userbot
    try:
        import userbot
        
        print(f"{GREEN}{'='*50}{RESET}")
        print(f"{YELLOW}UserBot запускается...{RESET}")
        print(f"{BLUE}Используйте /help в любом чате для просмотра доступных команд{RESET}")
        print(f"{YELLOW}Для выхода нажмите Ctrl+C{RESET}")
        print(f"{GREEN}{'='*50}{RESET}")
        
        await userbot.main()
        
    except ImportError as e:
        print(f"{RED}Ошибка импорта модуля userbot: {e}{RESET}")
        print(f"{YELLOW}Убедитесь, что файл userbot.py находится в текущем каталоге{RESET}")
        sys.exit(1)
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Работа прервана пользователем{RESET}")
    except Exception as e:
        print(f"{RED}Произошла ошибка: {e}{RESET}")
        logger.error(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Работа прервана пользователем{RESET}")
    
    print(f"{GREEN}UserBot завершил работу{RESET}")