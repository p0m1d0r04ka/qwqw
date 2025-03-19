from telethon import TelegramClient, events
from telethon.tl.functions.channels import GetFullChannelRequest
from datetime import datetime, timedelta
import config
import logging
from utils.helpers import is_admin, cleanup_message

logger = logging.getLogger(__name__)

def register_handlers(client: TelegramClient):
    """Register all stats command handlers"""
    
    @client.on(events.NewMessage(pattern=f"\\{config.CMD_PREFIX}chatstats"))
    async def chat_stats(event):
        """Command to show chat statistics"""
        try:
            # Check if stats are admin-only
            if config.STATS_ADMIN_ONLY and not await is_admin(client, event.chat_id, event.sender_id):
                await event.edit("🚫 Эта команда доступна только администраторам!")
                if config.CLEANUP_ENABLED:
                    await cleanup_message(client, event.message, config.CLEANUP_DELAY)
                return
            
            # Parse days argument
            days = 1  # Default to 1 day
            args = event.text.split()
            if len(args) > 1:
                try:
                    days = int(args[1])
                    if days < 1 or days > 30:  # Limit to 30 days
                        raise ValueError()
                except ValueError:
                    await event.edit(f"❗ Неверное количество дней. Использование: `{config.CMD_PREFIX}chatstats [1-30]`")
                    if config.CLEANUP_ENABLED:
                        await cleanup_message(client, event.message, config.CLEANUP_DELAY)
                    return
            
            # Get chat info
            chat = await event.get_chat()
            full_chat = await client(GetFullChannelRequest(chat))
            
            # Calculate stats
            since = datetime.now() - timedelta(days=days)
            messages = 0
            users = set()
            media = 0
            links = 0
            
            async for msg in client.iter_messages(chat.id, offset_date=since):
                messages += 1
                if msg.sender_id:
                    users.add(msg.sender_id)
                if msg.media:
                    media += 1
                if msg.entities:  # Count messages with links
                    for entity in msg.entities:
                        if entity.url:
                            links += 1
                            break
            
            # Prepare response
            stats = f"📊 **Статистика чата за {days} {'день' if days == 1 else 'дня' if 1 < days < 5 else 'дней'}:**\n\n"
            stats += f"👥 Участников: {full_chat.full_chat.participants_count}\n"
            stats += f"💬 Сообщений: {messages}\n"
            stats += f"👤 Активных пользователей: {len(users)}\n"
            stats += f"📷 Медиа сообщений: {media}\n"
            stats += f"🔗 Сообщений со ссылками: {links}\n"
            
            await event.edit(stats)
            
            if config.CLEANUP_ENABLED:
                await cleanup_message(client, event.message, config.CLEANUP_DELAY * 2)  # Give more time to read stats
                
        except Exception as e:
            logger.error(f"Error in chat_stats: {e}")
            await event.edit(f"❌ Произошла ошибка: {str(e)}")
    
    @client.on(events.NewMessage(pattern=f"\\{config.CMD_PREFIX}userstats"))
    async def user_stats(event):
        """Command to show user statistics"""
        try:
            # Check if stats are admin-only
            if config.STATS_ADMIN_ONLY and not await is_admin(client, event.chat_id, event.sender_id):
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
            if not replied:
                await event.edit("❌ Не удалось определить пользователя!")
                if config.CLEANUP_ENABLED:
                    await cleanup_message(client, event.message, config.CLEANUP_DELAY)
                return
            
            # Parse days argument
            days = 1  # Default to 1 day
            args = event.text.split()
            if len(args) > 1:
                try:
                    days = int(args[1])
                    if days < 1 or days > 30:  # Limit to 30 days
                        raise ValueError()
                except ValueError:
                    await event.edit(f"❗ Неверное количество дней. Использование: `{config.CMD_PREFIX}userstats [1-30]`")
                    if config.CLEANUP_ENABLED:
                        await cleanup_message(client, event.message, config.CLEANUP_DELAY)
                    return
            
            # Calculate stats
            since = datetime.now() - timedelta(days=days)
            messages = 0
            media = 0
            links = 0
            replies = 0
            
            async for msg in client.iter_messages(
                event.chat_id,
                from_user=replied.sender_id,
                offset_date=since
            ):
                messages += 1
                if msg.media:
                    media += 1
                if msg.entities:  # Count messages with links
                    for entity in msg.entities:
                        if entity.url:
                            links += 1
                            break
                if msg.reply_to:
                    replies += 1
            
            # Get user info
            user = await client.get_entity(replied.sender_id)
            mention = f"[{user.first_name}](tg://user?id={user.id})"
            
            # Prepare response
            stats = f"📊 **Статистика пользователя {mention} за {days} {'день' if days == 1 else 'дня' if 1 < days < 5 else 'дней'}:**\n\n"
            stats += f"💬 Сообщений: {messages}\n"
            stats += f"📷 Медиа: {media}\n"
            stats += f"🔗 Ссылок: {links}\n"
            stats += f"↩️ Ответов: {replies}\n"
            
            # Add admin status if applicable
            if await is_admin(client, event.chat_id, user.id):
                stats += "\n👑 Администратор"
            
            await event.edit(stats)
            
            if config.CLEANUP_ENABLED:
                await cleanup_message(client, event.message, config.CLEANUP_DELAY * 2)  # Give more time to read stats
                
        except Exception as e:
            logger.error(f"Error in user_stats: {e}")
            await event.edit(f"❌ Произошла ошибка: {str(e)}")