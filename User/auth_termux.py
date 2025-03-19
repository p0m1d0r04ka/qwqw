#!/usr/bin/env python3
"""
Скрипт для авторизации Telegram userbot в Termux
Этот скрипт запрашивает у пользователя данные для авторизации
и создает действительную сессию Telegram
"""

import os
import asyncio
import sys
import platform
from datetime import datetime
from getpass import getpass

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
        print("\033[91mОшибка: Этот скрипт предназначен только для запуска в Termux!\033[0m")
        print("\033[93mПожалуйста, установите Termux из F-Droid и запустите скрипт в нем:\033[0m")
        print("\033[93mhttps://f-droid.org/packages/com.termux/\033[0m")
        print("\033[93mИнструкции по установке: см. README.md\033[0m")
        return False
    return True

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
    print("Устанавливаем telethon, python-dotenv и cryptg...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "telethon", "python-dotenv", "cryptg"])
    print("Библиотеки установлены, запускаем скрипт снова.")
    os.execv(sys.executable, [sys.executable] + sys.argv)
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
        print(f"{BLUE}1. Войдите в аккаунт Telegram{RESET}")
        print(f"{BLUE}2. Перейдите в раздел 'API development tools'{RESET}")
        print(f"{BLUE}3. Создайте приложение, получите API ID и API Hash{RESET}")
        
        api_id = input(f"{GREEN}Введите ваш API ID: {RESET}")
        api_hash = input(f"{GREEN}Введите ваш API Hash: {RESET}")
        
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
            phone = input(f"{GREEN}Введите номер телефона (с кодом страны, например +7XXXXXXXXXX): {RESET}")
            await client.send_code_request(phone)
            
            # Ввод кода
            code = input(f"{GREEN}Введите код подтверждения, отправленный в Telegram: {RESET}")
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
            password = getpass(f"{GREEN}Введите пароль двухфакторной аутентификации: {RESET}")
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
    if not check_termux_environment():
        print(f"{RED}Этот скрипт предназначен для запуска только в Termux!{RESET}")
        sys.exit(1)
    
    print(f"{BLUE}Запуск в среде Termux{RESET}")
    
    # Проверка и создание .env файла при необходимости
    if check_env_file():
        print(f"{YELLOW}Создан новый файл .env. Перезагрузка...{RESET}")
    
    # Создание сессии
    try:
        if asyncio.run(create_session()):
            print(f"{GREEN}{BOLD}Сессия создана успешно!{RESET}")
            print(f"{BLUE}Теперь вы можете запустить UserBot с помощью ./start_userbot.sh{RESET}")
            return 0
        else:
            print(f"{RED}Не удалось создать сессию.{RESET}")
            return 1
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Операция прервана пользователем{RESET}")
        return 1

if __name__ == '__main__':
    sys.exit(main())