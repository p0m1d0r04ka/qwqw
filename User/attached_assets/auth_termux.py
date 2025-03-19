#!/usr/bin/env python3
"""
Скрипт для авторизации Telegram userbot в Termux
Этот скрипт запрашивает у пользователя данные для авторизации
и создает действительную сессию Telegram
"""

import os
import asyncio
import sys
from datetime import datetime
from getpass import getpass

# Проверка наличия необходимых библиотек
try:
    from telethon import TelegramClient
    from telethon.errors import (
        PhoneCodeInvalidError,
        PhoneCodeExpiredError,
        SessionPasswordNeededError,
        ApiIdInvalidError
    )
    from dotenv import load_dotenv
except ImportError:
    print("Отсутствуют необходимые библиотеки.")
    print("Устанавливаем telethon и python-dotenv...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "telethon", "python-dotenv"])
    print("Библиотеки установлены, запустите скрипт снова.")
    sys.exit(0)

# ANSI цвета для улучшения вывода в терминале
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'

# Проверка наличия .env файла
def check_env_file():
    """Проверка и создание .env файла при необходимости"""
    if not os.path.exists('.env'):
        print(f"{YELLOW}Файл .env не найден. Необходимо создать его.{RESET}")
        print(f"{BLUE}Для получения API ID и API Hash перейдите на https://my.telegram.org/apps{RESET}")
        
        api_id = input("Введите ваш API ID: ")
        api_hash = input("Введите ваш API Hash: ")
        
        with open('.env', 'w') as f:
            f.write(f"API_ID={api_id}\n")
            f.write(f"API_HASH={api_hash}\n")
        
        print(f"{GREEN}Файл .env создан успешно.{RESET}")
        return True
    return False

async def create_session():
    """Создание новой сессии Telegram"""
    # Загрузка переменных окружения из .env файла
    load_dotenv()
    
    # Получение API ID и API Hash
    api_id = os.environ.get('API_ID')
    api_hash = os.environ.get('API_HASH')
    
    if not api_id or not api_hash:
        check_env_file()
        load_dotenv()  # Перезагрузка после создания файла
        api_id = os.environ.get('API_ID')
        api_hash = os.environ.get('API_HASH')
    
    print(f"{GREEN}{BOLD}=== Создание сессии Telegram для UserBot ==={RESET}")
    print(f"{BLUE}Время: {datetime.now().strftime('%H:%M:%S')}{RESET}")
    print(f"{YELLOW}Для авторизации потребуется ввести номер телефона и код подтверждения{RESET}")
    
    # Проверка API данных
    if not api_id or not api_hash:
        print(f"{RED}API ID или API Hash не найдены в файле .env!{RESET}")
        sys.exit(1)
    
    # Создание клиента
    try:
        client = TelegramClient('userbot', api_id, api_hash)
        await client.connect()
        
        # Если уже авторизован
        if await client.is_user_authorized():
            me = await client.get_me()
            print(f"{GREEN}Авторизация уже выполнена{RESET}")
            print(f"{BLUE}Аккаунт: {me.first_name} (@{me.username}){RESET}")
            await client.disconnect()
            return True
        
        # Ввод номера телефона
        try:
            phone = input("Введите номер телефона (с кодом страны, например +7XXXXXXXXXX): ")
            await client.send_code_request(phone)
            
            # Ввод кода
            code = input("Введите код подтверждения: ")
            await client.sign_in(phone, code)
            
        except PhoneCodeInvalidError:
            print(f"{RED}Введен неверный код!{RESET}")
            await client.disconnect()
            return False
            
        except PhoneCodeExpiredError:
            print(f"{RED}Код подтверждения истек. Запустите скрипт снова.{RESET}")
            await client.disconnect()
            return False
            
        except SessionPasswordNeededError:
            # Если включена двухфакторная аутентификация
            print(f"{YELLOW}Требуется двухфакторная аутентификация{RESET}")
            password = getpass("Введите пароль двухфакторной аутентификации: ")
            await client.sign_in(password=password)
        
        # Проверка авторизации
        if await client.is_user_authorized():
            me = await client.get_me()
            print(f"{GREEN}Авторизация успешно выполнена!{RESET}")
            print(f"{BLUE}Аккаунт: {me.first_name} (@{me.username}){RESET}")
            await client.disconnect()
            return True
        else:
            print(f"{RED}Авторизация не удалась.{RESET}")
            await client.disconnect()
            return False
            
    except ApiIdInvalidError:
        print(f"{RED}Неверный API ID или API Hash. Проверьте файл .env{RESET}")
        return False
    except Exception as e:
        print(f"{RED}Произошла ошибка: {e}{RESET}")
        return False

def main():
    """Основная функция"""
    # Проверка запуска в Termux
    in_termux = os.path.exists('/data/data/com.termux')
    if in_termux:
        print(f"{BLUE}Запуск в среде Termux{RESET}")
    
    # Проверка и создание .env файла при необходимости
    if check_env_file():
        print(f"{YELLOW}Создан новый файл .env. Перезагрузка...{RESET}")
    
    # Создание сессии
    try:
        if asyncio.run(create_session()):
            print(f"{GREEN}{BOLD}Сессия создана успешно!{RESET}")
            print(f"{BLUE}Теперь вы можете запустить UserBot с помощью ./termux_start.sh{RESET}")
            return 0
        else:
            print(f"{RED}Не удалось создать сессию.{RESET}")
            return 1
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Операция прервана пользователем{RESET}")
        return 1

if __name__ == '__main__':
    sys.exit(main())