import os
import logging
from typing import Optional
from dotenv import load_dotenv
from datetime import timedelta

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG  # Changed to DEBUG for more detailed logs
)
logger = logging.getLogger(__name__)

# Load environment variables from .env file or attached_assets/.env
logger.info("Loading environment variables...")
if os.path.exists(".env"):
    load_dotenv()
elif os.path.exists("attached_assets/.env"):
    load_dotenv("attached_assets/.env")

# Log current working directory and .env file presence
cwd = os.getcwd()
env_file = os.path.join(cwd, '.env')
logger.info(f"Current working directory: {cwd}")
logger.info(f".env file exists: {os.path.exists(env_file)}")

# Telegram API Credentials
try:
    API_ID: Optional[int] = int(os.getenv("API_ID")) if os.getenv("API_ID") else None
    API_HASH: Optional[str] = os.getenv("API_HASH")

    if not API_ID or not API_HASH:
        raise ValueError("API credentials not found. Please check your .env file.")

    logger.info("Successfully loaded API credentials")
except ValueError as e:
    logger.error(f"Configuration Error: {e}")
    logger.info("Please make sure your .env file contains:")
    logger.info("API_ID=your_api_id")
    logger.info("API_HASH=your_api_hash")
    exit(1)
except Exception as e:
    logger.error(f"Unexpected error loading configuration: {e}")
    exit(1)

# Command prefix
CMD_PREFIX = "/"

# Command cooldown in seconds
COMMAND_COOLDOWN = 3

# Cleanup settings
CLEANUP_DELAY = 5  # Default delay for system message cleanup in seconds
CLEANUP_ENABLED = True  # Enable automatic cleanup of system messages

# Warning settings
MAX_WARNINGS = 3  # Maximum warnings before ban
WARNING_EXPIRY = timedelta(days=7)  # Warnings expire after 7 days

# Temporary mute durations (in minutes)
DEFAULT_MUTE_DURATION = 30  # Default mute time if not specified

# Session file path - prioritize existing session file
for session_path in ["userbot.session", "attached_assets/userbot.session"]:
    if os.path.exists(session_path):
        SESSION_NAME = session_path
        logger.info(f"Using session file: {SESSION_NAME}")
        break
else:
    SESSION_NAME = "userbot.session"
    logger.warning("No existing session file found, will create new one")

# Command descriptions for help
COMMANDS = {
    "help": "Показать список доступных команд",
    "ping": "Проверить работу бота",
    # Модерация
    "clear_all": "Очистить все сообщения в чате (только для админов)",
    "clear_user": "Очистить сообщения определенного пользователя (только для админов)",
    "ban": "Забанить пользователя (только для админов)",
    "mute": "Заглушить пользователя (только для админов)",
    "unmute": "Снять заглушение с пользователя (только для админов)", 
    "unban": "Разбанить пользователя (только для админов)",
    # Утилиты
    "mention_all": "Упомянуть всех пользователей в чате",
    "warn": "Выдать предупреждение пользователю (3 предупреждения = бан)",
    "tmute": "Временно заглушить пользователя (использование: /tmute <минуты>)",
    "purge": "Быстро удалить указанное количество сообщений (использование: /purge <количество>)",
    # Статистика
    "chatstats": "Показать статистику чата (использование: /chatstats [1-30] - количество дней)",
    "userstats": "Показать статистику пользователя (использование: /userstats [1-30] - количество дней)"
}

# In-memory storage for warnings
# Structure: {chat_id: {user_id: [timestamp1, timestamp2,...]}}
WARNINGS = {}

# Stats settings
STATS_ADMIN_ONLY = False  # False - любой пользователь может использовать статистику, True - только админы

# Web interface settings
WEB_PORT = 5000  # Port for the web interface
