from telethon import TelegramClient, events
from telethon.tl.functions.channels import EditBannedRequest
from telethon.tl.types import ChatBannedRights, User
from datetime import datetime, timedelta
import config
import logging
from utils.helpers import (
    is_admin, cleanup_message, get_current_warnings,
    add_warning, clear_warnings
)

logger = logging.getLogger(__name__)

def register_handlers(client: TelegramClient):
    """Register all moderation command handlers"""
    
    @client.on(events.NewMessage(pattern=f"\\{config.CMD_PREFIX}warn"))
    async def warn_user(event):
        """Command to warn a user"""
        try:
            # Check if sender is admin
            if not await is_admin(client, event.chat_id, event.sender_id):
                await event.edit("🚫 Эта команда доступна только администраторам!")
                if config.CLEANUP_ENABLED:
                    await cleanup_message(client, event.message, config.CLEANUP_DELAY)
                return
            
            # Get replied message
            if not event.is_reply:
                await event.edit("❗ Эта команда должна быть ответом на сообщение пользователя!")
                if config.CLEANUP_ENABLED:
                    await cleanup_message(client, event.message, config.CLEANUP_DELAY)
                return
            
            # Get message being replied to
            replied = await event.get_reply_message()
            if not replied or not isinstance(replied.sender, User):
                await event.edit("❌ Не удалось определить пользователя!")
                if config.CLEANUP_ENABLED:
                    await cleanup_message(client, event.message, config.CLEANUP_DELAY)
                return
            
            # Check if target is admin
            if await is_admin(client, event.chat_id, replied.sender.id):
                await event.edit("🚫 Нельзя выдать предупреждение администратору!")
                if config.CLEANUP_ENABLED:
                    await cleanup_message(client, event.message, config.CLEANUP_DELAY)
                return
            
            # Add warning
            warnings = add_warning(event.chat_id, replied.sender.id, config.WARNINGS)
            
            # Prepare response message
            user_mention = f"[{replied.sender.first_name}](tg://user?id={replied.sender.id})"
            response = f"⚠️ {user_mention} получил предупреждение ({warnings}/{config.MAX_WARNINGS})"
            
            # If max warnings reached, ban user
            if warnings >= config.MAX_WARNINGS:
                try:
                    rights = ChatBannedRights(
                        until_date=None,
                        view_messages=True,
                        send_messages=True,
                        send_media=True,
                        send_stickers=True,
                        send_gifs=True,
                        send_games=True,
                        send_inline=True,
                        embed_links=True
                    )
                    await client(EditBannedRequest(event.chat_id, replied.sender.id, rights))
                    response += "\n🔨 Пользователь забанен за превышение лимита предупреждений!"
                    clear_warnings(event.chat_id, replied.sender.id, config.WARNINGS)
                except Exception as e:
                    logger.error(f"Error banning user: {e}")
                    response += "\n❌ Не удалось забанить пользователя."
            
            await event.edit(response)
            if config.CLEANUP_ENABLED:
                await cleanup_message(client, event.message, config.CLEANUP_DELAY)
            
        except Exception as e:
            logger.error(f"Error in warn_user: {e}")
            await event.edit(f"❌ Произошла ошибка: {str(e)}")
    
    @client.on(events.NewMessage(pattern=f"\\{config.CMD_PREFIX}tmute"))
    async def tmute_user(event):
        """Command to temporarily mute a user"""
        try:
            # Check if sender is admin
            if not await is_admin(client, event.chat_id, event.sender_id):
                await event.edit("🚫 Эта команда доступна только администраторам!")
                if config.CLEANUP_ENABLED:
                    await cleanup_message(client, event.message, config.CLEANUP_DELAY)
                return
            
            # Get replied message
            if not event.is_reply:
                await event.edit("❗ Эта команда должна быть ответом на сообщение пользователя!")
                if config.CLEANUP_ENABLED:
                    await cleanup_message(client, event.message, config.CLEANUP_DELAY)
                return
            
            # Get message being replied to
            replied = await event.get_reply_message()
            if not replied or not isinstance(replied.sender, User):
                await event.edit("❌ Не удалось определить пользователя!")
                if config.CLEANUP_ENABLED:
                    await cleanup_message(client, event.message, config.CLEANUP_DELAY)
                return
            
            # Check if target is admin
            if await is_admin(client, event.chat_id, replied.sender.id):
                await event.edit("🚫 Нельзя заглушить администратора!")
                if config.CLEANUP_ENABLED:
                    await cleanup_message(client, event.message, config.CLEANUP_DELAY)
                return
            
            # Parse duration
            duration = config.DEFAULT_MUTE_DURATION
            args = event.text.split()
            if len(args) > 1:
                try:
                    duration = int(args[1])
                    if duration < 1:
                        raise ValueError()
                except ValueError:
                    await event.edit(f"❗ Неверная длительность. Использование: `{config.CMD_PREFIX}tmute <минуты>`")
                    if config.CLEANUP_ENABLED:
                        await cleanup_message(client, event.message, config.CLEANUP_DELAY)
                    return
            
            # Calculate unmute time
            until_date = datetime.now() + timedelta(minutes=duration)
            
            try:
                # Set restrictions
                rights = ChatBannedRights(
                    until_date=until_date,
                    send_messages=True,
                    send_media=True,
                    send_stickers=True,
                    send_gifs=True,
                    send_games=True,
                    send_inline=True
                )
                await client(EditBannedRequest(event.chat_id, replied.sender.id, rights))
                
                # Prepare response
                user_mention = f"[{replied.sender.first_name}](tg://user?id={replied.sender.id})"
                response = f"🔇 {user_mention} заглушен на {duration} минут"
                
                await event.edit(response)
                
            except Exception as e:
                logger.error(f"Error muting user: {e}")
                await event.edit(f"❌ Не удалось заглушить пользователя: {str(e)}")
            
            if config.CLEANUP_ENABLED:
                await cleanup_message(client, event.message, config.CLEANUP_DELAY)
                
        except Exception as e:
            logger.error(f"Error in tmute_user: {e}")
            await event.edit(f"❌ Произошла ошибка: {str(e)}")