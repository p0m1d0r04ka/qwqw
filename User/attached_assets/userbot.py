import logging
import sys
import os
import getpass
from telethon import TelegramClient, events
from telethon.errors import SessionPasswordNeededError, PhoneCodeInvalidError
import asyncio
from datetime import datetime, timedelta
import config
from utils.helpers import cleanup_message, is_admin
import admin
import utils
import stats
import moderation
# Импортируем модуль для команд логов и управления пользователями
import log_management
# Настраиваем логирование
log_management.setup_logging()
from plugins import load_plugins

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Command cooldown storage
command_timestamps = {}

def check_cooldown(user_id: int) -> bool:
    """Check if user can execute command based on cooldown"""
    if user_id not in command_timestamps:
        command_timestamps[user_id] = datetime.now()
        return True

    last_command = command_timestamps[user_id]
    if datetime.now() - last_command < timedelta(seconds=config.COMMAND_COOLDOWN):
        return False

    command_timestamps[user_id] = datetime.now()
    return True

async def setup_session(client):
    """Setup Telegram session with handling for 2FA"""
    # Connect to Telegram
    await client.connect()
    
    # Check if already authorized
    if not await client.is_user_authorized():
        print("Требуется авторизация в Telegram")
        
        # Ask for phone number
        phone = input("Введите номер телефона (с кодом страны, например +7XXXXXXXXXX): ")
        
        try:
            # Send code request
            await client.send_code_request(phone)
            
            # Ask for verification code
            code = input("Введите код подтверждения из Telegram: ")
            
            try:
                # Try to sign in with code
                await client.sign_in(phone, code)
            except SessionPasswordNeededError:
                # 2FA is enabled
                print("Обнаружена двухфакторная аутентификация")
                password = getpass.getpass("Введите свой пароль 2FA: ")
                await client.sign_in(password=password)
            
            print("Авторизация успешна!")
            
        except PhoneCodeInvalidError:
            print("Ошибка: Неверный код подтверждения")
            sys.exit(1)
        except Exception as e:
            print(f"Ошибка при авторизации: {e}")
            sys.exit(1)

async def main():
    print("=== Telegram UserBot ===")
    print("Запуск...")
    
    # Initialize client
    logger.info(f"Using session file: {config.SESSION_NAME}")
    logger.info("Initializing Telegram client...")

    try:
        # Clear existing session file on start to avoid multi-IP session issues
        if os.path.exists(config.SESSION_NAME):
            try:
                logger.info(f"Removing existing session file to avoid multi-IP issues: {config.SESSION_NAME}")
                os.remove(config.SESSION_NAME)
            except Exception as e:
                logger.warning(f"Failed to remove session file: {e}")
                
        # Create new client with updated initialization
        # Используем улучшенные параметры для исправления проблем
        # с подключением с разных IP и обработкой ошибок
        client = TelegramClient(
            config.SESSION_NAME,
            config.API_ID,
            config.API_HASH,
            device_model="Console UserBot",
            system_version="1.0",
            app_version="1.0",
            auto_reconnect=True,
            retry_delay=1,
            connection_retries=10,
            flood_sleep_threshold=60    # Увеличиваем порог ожидания при флуде
            # Убираем неподдерживаемые параметры для текущей версии Telethon
        )

        # Setup session if needed
        await setup_session(client)
        
        # Register command handlers
        @client.on(events.NewMessage(pattern=f"\\{config.CMD_PREFIX}help"))
        async def help_handler(event):
            logger.debug(f"Received help command from user {event.sender_id}")
            if not check_cooldown(event.sender_id):
                return

            help_text = "**Доступные команды:**\n\n"
            for cmd, desc in config.COMMANDS.items():
                help_text += f"`{config.CMD_PREFIX}{cmd}`: {desc}\n"

            try:
                await event.reply(help_text)
                logger.debug("Help message sent successfully")
            except Exception as e:
                logger.error(f"Error sending help message: {e}")

        @client.on(events.NewMessage(pattern=f"\\{config.CMD_PREFIX}ping"))
        async def ping_handler(event):
            logger.debug(f"Received ping command from user {event.sender_id}")
            if not check_cooldown(event.sender_id):
                return

            try:
                start = datetime.now()
                message = await event.reply("**Понг!**")
                end = datetime.now()

                ms = (end - start).microseconds / 1000
                await message.edit(f"**Понг!** Время ответа: `{ms:.2f}мс`")
                logger.debug("Ping response sent successfully")
            except Exception as e:
                logger.error(f"Error handling ping command: {e}")

        # Register handlers from modules
        print("Регистрация обработчиков команд...")
        admin.register_handlers(client)
        utils.register_handlers(client)
        stats.register_handlers(client)
        moderation.register_handlers(client)
        log_management.register_handlers(client)

        # Load and register plugins
        print("Загрузка плагинов...")
        plugins = load_plugins(client)
        plugin_count = 0
        for plugin in plugins:
            try:
                plugin.register_handlers()
                plugin_count += 1
            except Exception as e:
                logger.error(f"Error registering handlers for plugin {plugin}: {e}")
        
        print(f"Загружено плагинов: {plugin_count}")

        # Start client
        print("Подключение к Telegram...")
        await client.start()
        
        # Log in which mode we're running
        me = await client.get_me()
        print(f"\n=== UserBot запущен ===")
        print(f"Работает как: {me.first_name} (@{me.username})")
        print(f"Доступно команд: {len(config.COMMANDS)}")
        print("Для завершения работы нажмите Ctrl+C")
        print("=" * 30)
        
        # Keep the bot running
        await client.run_until_disconnected()

    except KeyboardInterrupt:
        print("\nРабота UserBot остановлена пользователем")
    except SessionPasswordNeededError:
        logger.error("Ошибка: Требуется 2FA аутентификация")
        print("Запустите скрипт снова и введите пароль 2FA при запросе")
        sys.exit(1)
    except ConnectionError as e:
        logger.error(f"Ошибка подключения: {e}")
        print("Проверьте подключение к интернету")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Ошибка запуска UserBot: {e}")
        
        # Обработка конкретной ошибки с сессией
        error_str = str(e).lower()
        if "session" in error_str and "no longer valid" in error_str:
            print(f"Ошибка сессии: {e}")
            print("Сессия недействительна из-за смены IP адреса или региона.")
            print("Будет создана новая сессия при следующем запуске.")
            
            # Удаляем файл сессии для создания нового при следующем запуске
            try:
                session_file = f"{config.SESSION_NAME}.session"
                if os.path.exists(session_file):
                    os.remove(session_file)
                    print(f"Файл сессии {session_file} удален.")
                else:
                    print(f"Файл сессии {session_file} не найден.")
            except Exception as se:
                print(f"Не удалось удалить файл сессии: {se}")
                
            sys.exit(1)
        elif "authoriz" in error_str or "auth" in error_str:
            print("Ошибка авторизации. Пожалуйста, запустите скрипт снова для повторной авторизации.")
            sys.exit(1)
        else:
            print(f"Критическая ошибка: {e}")
            sys.exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nРабота UserBot прервана")
    except Exception as e:
        print(f"Непредвиденная ошибка: {e}")
        sys.exit(1)
