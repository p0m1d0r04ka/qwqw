from telethon import TelegramClient, events
from telethon.tl.functions.channels import EditBannedRequest
from telethon.tl.types import ChatBannedRights, User
import config
import logging
from utils.helpers import is_admin, cleanup_message

logger = logging.getLogger(__name__)

def register_handlers(client: TelegramClient):
    """Register all admin command handlers"""
    
    @client.on(events.NewMessage(pattern=f"\\{config.CMD_PREFIX}ban"))
    async def ban_user(event):
        """Command to ban a user"""
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
                await event.edit("🚫 Нельзя забанить администратора!")
                if config.CLEANUP_ENABLED:
                    await cleanup_message(client, event.message, config.CLEANUP_DELAY)
                return
            
            try:
                # Set ban rights
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
                
                # Prepare response
                user_mention = f"[{replied.sender.first_name}](tg://user?id={replied.sender.id})"
                response = f"🔨 {user_mention} забанен"
                
                await event.edit(response)
                
            except Exception as e:
                logger.error(f"Error banning user: {e}")
                await event.edit(f"❌ Не удалось забанить пользователя: {str(e)}")
            
            if config.CLEANUP_ENABLED:
                await cleanup_message(client, event.message, config.CLEANUP_DELAY)
                
        except Exception as e:
            logger.error(f"Error in ban_user: {e}")
            await event.edit(f"❌ Произошла ошибка: {str(e)}")
    
    @client.on(events.NewMessage(pattern=f"\\{config.CMD_PREFIX}unban"))
    async def unban_user(event):
        """Command to unban a user"""
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
            
            try:
                # Set unban rights
                rights = ChatBannedRights(
                    until_date=None,
                    view_messages=False,
                    send_messages=False,
                    send_media=False,
                    send_stickers=False,
                    send_gifs=False,
                    send_games=False,
                    send_inline=False,
                    embed_links=False
                )
                await client(EditBannedRequest(event.chat_id, replied.sender.id, rights))
                
                # Prepare response
                user_mention = f"[{replied.sender.first_name}](tg://user?id={replied.sender.id})"
                response = f"✅ {user_mention} разбанен"
                
                await event.edit(response)
                
            except Exception as e:
                logger.error(f"Error unbanning user: {e}")
                await event.edit(f"❌ Не удалось разбанить пользователя: {str(e)}")
            
            if config.CLEANUP_ENABLED:
                await cleanup_message(client, event.message, config.CLEANUP_DELAY)
                
        except Exception as e:
            logger.error(f"Error in unban_user: {e}")
            await event.edit(f"❌ Произошла ошибка: {str(e)}")
    
    @client.on(events.NewMessage(pattern=f"\\{config.CMD_PREFIX}mute"))
    async def mute_user(event):
        """Command to mute a user"""
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
            
            try:
                # Set mute rights
                rights = ChatBannedRights(
                    until_date=None,
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
                response = f"🔇 {user_mention} заглушен"
                
                await event.edit(response)
                
            except Exception as e:
                logger.error(f"Error muting user: {e}")
                await event.edit(f"❌ Не удалось заглушить пользователя: {str(e)}")
            
            if config.CLEANUP_ENABLED:
                await cleanup_message(client, event.message, config.CLEANUP_DELAY)
                
        except Exception as e:
            logger.error(f"Error in mute_user: {e}")
            await event.edit(f"❌ Произошла ошибка: {str(e)}")
    
    @client.on(events.NewMessage(pattern=f"\\{config.CMD_PREFIX}unmute"))
    async def unmute_user(event):
        """Command to unmute a user"""
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
            
            try:
                # Set unmute rights
                rights = ChatBannedRights(
                    until_date=None,
                    send_messages=False,
                    send_media=False,
                    send_stickers=False,
                    send_gifs=False,
                    send_games=False,
                    send_inline=False
                )
                await client(EditBannedRequest(event.chat_id, replied.sender.id, rights))
                
                # Prepare response
                user_mention = f"[{replied.sender.first_name}](tg://user?id={replied.sender.id})"
                response = f"🔊 {user_mention} разглушен"
                
                await event.edit(response)
                
            except Exception as e:
                logger.error(f"Error unmuting user: {e}")
                await event.edit(f"❌ Не удалось разглушить пользователя: {str(e)}")
            
            if config.CLEANUP_ENABLED:
                await cleanup_message(client, event.message, config.CLEANUP_DELAY)
                
        except Exception as e:
            logger.error(f"Error in unmute_user: {e}")
            await event.edit(f"❌ Произошла ошибка: {str(e)}")