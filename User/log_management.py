from telethon import TelegramClient, events
import config
import logging
import os
import asyncio
from datetime import datetime
from utils.helpers import is_admin, cleanup_message, refresh_admin_cache, get_user_count

logger = logging.getLogger(__name__)

def setup_logging():
    """Setup file logging with rotation"""
    from logging.handlers import RotatingFileHandler
    
    # Create log directory if it doesn't exist
    log_dir = os.path.dirname(config.LOG_FILE)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Create file handler for logging
    file_handler = RotatingFileHandler(
        config.LOG_FILE,
        maxBytes=config.LOG_MAX_BYTES,
        backupCount=config.LOG_BACKUP_COUNT
    )
    
    # Set the format for the logs
    formatter = logging.Formatter(config.LOG_FORMAT)
    file_handler.setFormatter(formatter)
    
    # Get the root logger and add the handler
    root_logger = logging.getLogger()
    root_logger.setLevel(config.LOG_LEVEL)
    root_logger.addHandler(file_handler)
    
    logger.info("Logging system initialized")

def register_handlers(client: TelegramClient):
    @client.on(events.NewMessage(pattern=f"\\{config.CMD_PREFIX}log"))
    async def log_command(event):
        """Command to view bot logs"""
        try:
            # Check if sender is admin
            if not await is_admin(client, event.chat_id, event.sender_id):
                await event.edit("Эта команда доступна только админам!")
                if config.CLEANUP_ENABLED:
                    await cleanup_message(client, event.message, config.CLEANUP_DELAY)
                return
            
            # Parse arguments
            args = event.text.split()
            lines = config.LOG_MAX_DISPLAY_LINES  # Default line count
            
            if len(args) > 1:
                try:
                    lines = int(args[1])
                    if lines < 1 or lines > 100:  # Limit to avoid long messages
                        raise ValueError()
                except ValueError:
                    await event.edit(f"Неверное количество строк. Использование: `{config.CMD_PREFIX}log [1-100]`")
                    if config.CLEANUP_ENABLED:
                        await cleanup_message(client, event.message, config.CLEANUP_DELAY)
                    return
            
            # Check if log file exists
            if not os.path.exists(config.LOG_FILE):
                await event.edit("Файл логов не найден. Бот еще не создал логи.")
                if config.CLEANUP_ENABLED:
                    await cleanup_message(client, event.message, config.CLEANUP_DELAY)
                return
            
            # Read the log file
            with open(config.LOG_FILE, "r") as f:
                log_lines = f.readlines()
            
            # Get last N lines
            last_lines = log_lines[-lines:] if len(log_lines) >= lines else log_lines
            
            # Format the output
            log_output = f"**📋 Последние {len(last_lines)} строк лога:**\n\n```\n"
            log_output += "".join(last_lines)
            log_output += "\n```"
            
            # Check if output is too long
            if len(log_output) > 4000:
                # Truncate message to fit Telegram limits
                log_output = log_output[:3997] + "..."
            
            await event.edit(log_output)
            
            # Add info about log file
            file_size = os.path.getsize(config.LOG_FILE) / 1024  # KB
            await event.respond(f"📊 **Информация о логах**\n"
                              f"📁 Файл: `{config.LOG_FILE}`\n"
                              f"📏 Размер: {file_size:.2f} KB\n"
                              f"🕒 Последнее обновление: {datetime.fromtimestamp(os.path.getmtime(config.LOG_FILE)).strftime('%Y-%m-%d %H:%M:%S')}")
            
        except Exception as e:
            logger.error(f"Error in log_command: {e}")
            await event.edit(f"Ошибка при чтении логов: {str(e)}")
    
    @client.on(events.NewMessage(pattern=f"\\{config.CMD_PREFIX}users"))
    async def users_command(event):
        """Command to refresh users and admin list for the chat"""
        try:
            # Check if sender is admin
            if not await is_admin(client, event.chat_id, event.sender_id):
                await event.edit("Эта команда доступна только админам!")
                if config.CLEANUP_ENABLED:
                    await cleanup_message(client, event.message, config.CLEANUP_DELAY)
                return
            
            # Inform user that the operation has started
            await event.edit("🔄 Обновление списка пользователей и администраторов...")
            
            # Get the chat entity
            chat = await client.get_entity(event.chat_id)
            chat_title = getattr(chat, 'title', f"Chat {event.chat_id}")
            
            # Refresh admin cache
            admin_count, success = await refresh_admin_cache(client, event.chat_id)
            
            if not success:
                await event.edit("❌ Ошибка при обновлении списка администраторов!")
                if config.CLEANUP_ENABLED:
                    await cleanup_message(client, event.message, config.CLEANUP_DELAY)
                return
            
            # Count total users (this might take time for large chats)
            total_users = await get_user_count(client, event.chat_id)
            
            # Prepare and send the result message
            result = f"✅ **Обновление завершено!**\n\n"
            result += f"**📊 Информация о чате: {chat_title}**\n"
            result += f"👥 Всего пользователей: {total_users}\n"
            result += f"👑 Администраторов: {admin_count}\n\n"
            result += "Теперь следующие команды будут работать с обновленным списком:\n"
            result += "`/ban`, `/unban`, `/warn`, `/unwarn`, `/mute`, `/unmute`, `/userstats`, и другие."
            
            await event.edit(result)
            
            # Log the result
            logger.info(f"Users updated for chat {event.chat_id}: {admin_count} admins, {total_users} total users")
            
        except Exception as e:
            logger.error(f"Error in users_command: {e}")
            await event.edit(f"Ошибка при обновлении списка пользователей: {str(e)}")