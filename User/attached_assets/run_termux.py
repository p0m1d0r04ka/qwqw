#!/usr/bin/env python3
import os
import sys
import logging
import time
import signal
import subprocess
import platform
import asyncio
from telethon import TelegramClient, events
from telethon.errors import SessionPasswordNeededError, PhoneNumberInvalidError

# ANSI цвета для красивого вывода
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
logger = logging.getLogger("TermuxLauncher")

def check_environment():
    """Проверка и настройка окружения"""
    print(f"{YELLOW}Проверка системы...{RESET}")
    
    # Информация о системе
    system_info = f"{platform.system()} {platform.release()}"
    print(f"{BLUE}Платформа: {system_info}{RESET}")
    
    # Проверка на Termux
    is_termux = False
    if os.path.exists("/data/data/com.termux"):
        is_termux = True
        print(f"{GREEN}Обнаружена среда Termux{RESET}")
    
    # Проверка сессии
    session_exists = os.path.exists("userbot.session")
    
    # Проверка API-данных
    api_configured = False
    
    # Загружаем .env, если существует
    if os.path.exists(".env"):
        # Загружаем переменные окружения из .env
        with open(".env", "r") as env_file:
            for line in env_file:
                if "=" in line:
                    key, value = line.strip().split("=", 1)
                    os.environ[key] = value
        
        api_id = os.getenv("API_ID", "")
        api_hash = os.getenv("API_HASH", "")
        
        if api_id and api_hash:
            api_configured = True
            print(f"{GREEN}API-данные настроены успешно{RESET}")
        else:
            print(f"{YELLOW}API-данные не найдены в .env файле{RESET}")
    else:
        print(f"{YELLOW}Файл .env не найден{RESET}")
    
    # Проверка авторизации
    if not session_exists or not api_configured:
        print(f"{RED}Не найдена активная сессия Telegram или API-данные{RESET}")
        print(f"{YELLOW}Запустите скрипт авторизации командой:{RESET}")
        print(f"{BLUE}python auth_termux.py{RESET}")
        
        if not os.path.exists("auth_termux.py"):
            print(f"{RED}Скрипт auth_termux.py не найден!{RESET}")
            print(f"{YELLOW}Проверьте, правильно ли установлены файлы.{RESET}")
        
        sys.exit(1)
    
    # Успешная проверка
    print(f"{GREEN}Все необходимые файлы найдены{RESET}")
    
    return is_termux

async def check_session():
    """Проверка валидности сессии"""
    print(f"{YELLOW}Проверка сессии Telegram...{RESET}")
    
    # Получаем API данные из .env
    api_id = os.getenv("API_ID", "")
    api_hash = os.getenv("API_HASH", "")
    
    if not api_id or not api_hash:
        print(f"{RED}API-данные не настроены{RESET}")
        return False
    
    try:
        # Создаем клиент для проверки сессии
        client = TelegramClient(
            "userbot",
            api_id,
            api_hash,
            device_model="Termux Userbot",
            system_version="1.0",
            app_version="1.0"
        )
        
        # Подключаемся и проверяем авторизацию
        await client.connect()
        
        if await client.is_user_authorized():
            me = await client.get_me()
            print(f"{GREEN}Сессия действительна! Авторизованы как {me.first_name}{RESET}")
            if me.username:
                print(f"{GREEN}@{me.username}{RESET}")
            
            # Закрываем соединение
            await client.disconnect()
            return True
        else:
            print(f"{RED}Сессия недействительна или устарела{RESET}")
            print(f"{YELLOW}Пожалуйста, повторите авторизацию:{RESET}")
            print(f"{BLUE}python auth_termux.py{RESET}")
            
            # Закрываем соединение
            await client.disconnect()
            return False
    
    except Exception as e:
        print(f"{RED}Ошибка при проверке сессии: {e}{RESET}")
        logger.error(f"Session check error: {e}")
        return False

def run_userbot():
    """Запуск userbot"""
    try:
        print(f"{GREEN}{BOLD}Запуск Telegram userbot...{RESET}")
        userbot_process = subprocess.Popen(
            ["python", "userbot.py"],
            stdout=subprocess.PIPE, 
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        # Вывод логов в реальном времени
        print(f"{YELLOW}Userbot запущен, отображение логов:{RESET}")
        for line in userbot_process.stdout:
            # Подсветка для разных типов логов
            if "ERROR" in line:
                sys.stdout.write(f"{RED}{line}{RESET}")
            elif "WARNING" in line:
                sys.stdout.write(f"{YELLOW}{line}{RESET}")
            elif "INFO" in line:
                sys.stdout.write(f"{GREEN}{line}{RESET}")
            else:
                sys.stdout.write(line)
            sys.stdout.flush()
        
        # Если процесс завершился
        userbot_process.wait()
        if userbot_process.returncode != 0:
            print(f"{RED}Userbot завершился с ошибкой (код {userbot_process.returncode}){RESET}")
            return False
        
        return True
    except Exception as e:
        print(f"{RED}Ошибка при запуске userbot: {e}{RESET}")
        logger.error(f"Error starting userbot: {e}")
        return False

def handle_signal(signum, frame):
    """Обработка сигналов для корректного завершения"""
    print(f"{YELLOW}Получен сигнал завершения, остановка userbot...{RESET}")
    sys.exit(0)

async def main_async():
    """Асинхронная часть основной функции"""
    # Проверка сессии
    session_valid = await check_session()
    if not session_valid:
        sys.exit(1)
    return True

def main():
    """Основная функция"""
    print(f"{GREEN}{BOLD}===== Telegram Userbot для Termux ====={RESET}")
    
    # Настройка обработчиков сигналов
    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)
    
    # Проверка окружения
    is_termux = check_environment()
    
    # Проверка сессии
    if not asyncio.run(main_async()):
        return
    
    # Применяем специфичные для Termux настройки
    if is_termux:
        # Termux может иметь ограничения на ресурсы, увеличиваем лимиты
        os.environ["PYTHONOPTIMIZE"] = "1"  # Оптимизация памяти
        print(f"{BLUE}Применены оптимизации для Termux{RESET}")
    
    # Постоянно перезапускаем userbot в случае падения
    retry_count = 0
    print(f"{YELLOW}Режим автоперезапуска активирован{RESET}")
    
    while True:
        success = run_userbot()
        if not success:
            retry_count += 1
            if retry_count > 5:
                print(f"{RED}Слишком много ошибок запуска ({retry_count}). Проверьте интернет-соединение.{RESET}")
                retry_count = 0
                wait_time = 30
            else:
                wait_time = 10
                
            print(f"{YELLOW}Userbot завершился с ошибкой, перезапуск через {wait_time} секунд...{RESET}")
            print(f"{BLUE}Для принудительного выхода нажмите Ctrl+C{RESET}")
            time.sleep(wait_time)
        else:
            print(f"{YELLOW}Userbot завершил работу, перезапуск через 3 секунды...{RESET}")
            retry_count = 0
            time.sleep(3)

if __name__ == "__main__":
    main()