import os
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API credentials
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")

# Bot settings
SESSION_NAME = "userbot"
CMD_PREFIX = "/"  # Command prefix
COMMAND_COOLDOWN = 3  # Seconds between commands

# Moderation settings
MAX_WARNINGS = 3  # Number of warnings before ban
DEFAULT_MUTE_DURATION = 60  # Default mute duration in minutes
WARNINGS = {}  # Store warnings for users

# Admin settings
ADMINS_CACHE = {}  # Cache for admin users in chats
ADMIN_CACHE_TTL = 1800  # Cache TTL in seconds (30 minutes)

# Cleanup settings
CLEANUP_ENABLED = True  # Auto-delete command messages
CLEANUP_DELAY = 5  # Seconds before cleanup

# Stats settings
STATS_ADMIN_ONLY = False  # Whether stats commands are admin-only

# Log settings
LOG_FILE = "userbot.log"
LOG_MAX_BYTES = 1024 * 1024 * 5  # 5 MB
LOG_BACKUP_COUNT = 3
LOG_LEVEL = logging.INFO
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_MAX_DISPLAY_LINES = 50  # Maximum number of log lines to display

# Available commands list
COMMANDS = {
    "help": "Показать это сообщение",
    "ping": "Проверить время отклика бота",
    "warn": "Выдать предупреждение пользователю",
    "tmute": "Временно заглушить пользователя",
    "chatstats": "Показать статистику чата",
    "userstats": "Показать статистику пользователя",
    "mention_all": "Упомянуть всех участников чата",
    "log": "Просмотр логов работы бота",
    "users": "Обновить список пользователей чата"
}