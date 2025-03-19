from telethon import TelegramClient, events
from telethon.tl.functions.channels import GetFullChannelRequest
from collections import Counter
import config
import logging
from datetime import datetime, timedelta
import time
from utils.helpers import is_admin, cleanup_message, check_user_is_not_admin

logger = logging.getLogger(__name__)

def register_handlers(client: TelegramClient):
    @client.on(events.NewMessage(pattern=f"\\{config.CMD_PREFIX}chatstats"))
    async def chat_stats(event):
        try:
            # Check if user has permission (admin check is optional for stats)
            if config.STATS_ADMIN_ONLY and not await is_admin(client, event.chat_id, event.sender_id):
                await event.edit("Эта команда доступна только админам!")
                if config.CLEANUP_ENABLED:
                    await cleanup_message(client, event.message, config.CLEANUP_DELAY)
                return

            # Parse arguments
            args = event.text.split()
            days = 1  # Default 1 day
            if len(args) > 1:
                try:
                    days = int(args[1])
                    if days < 1 or days > 30:  # Limit to avoid long processing
                        raise ValueError()
                except ValueError:
                    await event.edit(f"Неверное число дней. Использование: `{config.CMD_PREFIX}chatstats [1-30]`")
                    if config.CLEANUP_ENABLED:
                        await cleanup_message(client, event.message, config.CLEANUP_DELAY)
                    return

            # Start time for performance measurement
            start_time = time.time()
            
            # Inform user that stats are being collected
            await event.edit(f"Собираю статистику чата за последние {days} {'день' if days == 1 else 'дня' if 1 < days < 5 else 'дней'}...")
            
            # Get messages from specified time period
            time_period = datetime.now() - timedelta(days=days)

            # Initialize counters
            message_count = 0
            user_activity = Counter()
            media_count = 0
            message_types = Counter()

            # Get chat info
            chat_entity = await client.get_entity(event.chat_id)
            chat_info = None
            try:
                if hasattr(chat_entity, 'megagroup') and chat_entity.megagroup:
                    # Get full channel info if it's a supergroup
                    full_chat = await client(GetFullChannelRequest(chat_entity))
                    chat_info = full_chat.full_chat
            except Exception as e:
                logger.warning(f"Could not get full chat info: {e}")

            # Process messages
            async for message in client.iter_messages(
                event.chat_id,
                offset_date=time_period,
                limit=10000  # Reasonable limit to avoid long processing
            ):
                message_count += 1
                if message.sender_id:
                    user_activity[message.sender_id] += 1
                
                # Count media types
                if message.media:
                    media_count += 1
                    if hasattr(message.media, '__class__'):
                        media_type = message.media.__class__.__name__
                        message_types[media_type] += 1
                else:
                    message_types["Text"] += 1
            
            # Calculate active hours (by message timestamp)
            hour_activity = Counter()
            async for message in client.iter_messages(
                event.chat_id,
                offset_date=time_period,
                limit=1000  # Smaller limit for performance
            ):
                if message.date:
                    hour = message.date.hour
                    hour_activity[hour] += 1
            
            # Get top active hours
            most_active_hours = hour_activity.most_common(3)
            active_hours_str = ", ".join([f"{hour}:00-{hour+1}:00" for hour, _ in most_active_hours])

            # Get top 5 active users
            top_users = []
            for user_id, count in user_activity.most_common(5):
                try:
                    user = await client.get_entity(user_id)
                    name = user.first_name
                    if hasattr(user, 'username') and user.username:
                        name += f" (@{user.username})"
                    top_users.append(f"{name}: {count} сообщений")
                except Exception as e:
                    logger.warning(f"Could not get user info for {user_id}: {e}")
                    top_users.append(f"ID{user_id}: {count} сообщений")

            # Format statistics
            period_text = f"за последние {days} {'день' if days == 1 else 'дня' if 1 < days < 5 else 'дней'}"
            stats = f"**📊 Статистика чата {period_text}:**\n\n"
            
            if hasattr(chat_entity, 'title'):
                stats += f"**Чат:** {chat_entity.title}\n"
            
            stats += f"**Всего сообщений:** {message_count}\n"
            stats += f"**Активных пользователей:** {len(user_activity)}\n"
            stats += f"**Медиа сообщений:** {media_count} ({round(media_count/message_count*100, 1)}%)\n"
            
            if chat_info and hasattr(chat_info, 'members_count'):
                stats += f"**Всего участников:** {chat_info.members_count}\n"
            
            stats += f"**Самые активные часы:** {active_hours_str}\n\n"
            
            stats += "**Топ 5 активных пользователей:**\n"
            stats += "\n".join(f"• {user}" for user in top_users)
            
            # Add top message types if any
            if message_types:
                stats += "\n\n**Типы сообщений:**\n"
                for msg_type, count in message_types.most_common(3):
                    stats += f"• {msg_type}: {count} ({round(count/message_count*100, 1)}%)\n"
            
            # Add processing time
            processing_time = round(time.time() - start_time, 2)
            stats += f"\n⏱ Время обработки: {processing_time} сек."

            await event.edit(stats)
        except Exception as e:
            logger.error(f"Error in chat_stats: {e}")
            await event.edit(f"Не удалось получить статистику чата: {str(e)}")

    @client.on(events.NewMessage(pattern=f"\\{config.CMD_PREFIX}userstats"))
    async def user_stats(event):
        try:
            # Check if sender is admin (optional for stats)
            if config.STATS_ADMIN_ONLY and not await is_admin(client, event.chat_id, event.sender_id):
                await event.edit("Эта команда доступна только админам!")
                if config.CLEANUP_ENABLED:
                    await cleanup_message(client, event.message, config.CLEANUP_DELAY)
                return

            # Parse arguments
            args = event.text.split()
            days = 7  # Default 7 days
            if len(args) > 1 and not event.reply_to_msg_id:
                try:
                    days = int(args[1])
                    if days < 1 or days > 30:  # Limit to prevent long processing
                        raise ValueError()
                except ValueError:
                    await event.edit(f"Неверное число дней. Использование: `{config.CMD_PREFIX}userstats [1-30]`")
                    if config.CLEANUP_ENABLED:
                        await cleanup_message(client, event.message, config.CLEANUP_DELAY)
                    return

            # Determine target user ID
            target_user_id = None
            if event.reply_to_msg_id:
                replied_msg = await event.get_reply_message()
                target_user_id = replied_msg.sender_id
            else:
                # Default to the user's own stats if no reply
                target_user_id = event.sender_id

            # Inform user that stats are being collected
            time_period = datetime.now() - timedelta(days=days)
            await event.edit(f"Собираю статистику пользователя за последние {days} {'день' if days == 1 else 'дня' if 1 < days < 5 else 'дней'}...")

            # Get user info
            user = await client.get_entity(target_user_id)

            # Calculate statistics
            message_count = 0
            media_count = 0
            reply_count = 0
            message_types = Counter()
            hour_activity = Counter()

            # First pass to count messages and types
            async for message in client.iter_messages(
                event.chat_id,
                from_user=target_user_id,
                offset_date=time_period,
                limit=1000  # Reasonable limit to avoid long processing
            ):
                message_count += 1
                
                # Count media types
                if message.media:
                    media_count += 1
                    if hasattr(message.media, '__class__'):
                        media_type = message.media.__class__.__name__
                        message_types[media_type] += 1
                else:
                    message_types["Text"] += 1
                
                # Count replies to this user's messages
                if message.replies and message.replies.replies:
                    reply_count += message.replies.replies
                
                # Track activity by hour
                if message.date:
                    hour = message.date.hour
                    hour_activity[hour] += 1

            # Find most active hours
            most_active_hours = hour_activity.most_common(2)
            active_hours_str = ", ".join([f"{hour}:00-{hour+1}:00" for hour, _ in most_active_hours]) if most_active_hours else "Недостаточно данных"

            # Get chat participation percentage
            total_chat_messages = 0
            async for _ in client.iter_messages(
                event.chat_id,
                offset_date=time_period,
                limit=5000  # Higher limit to get a better sample
            ):
                total_chat_messages += 1
            
            participation_pct = 0
            if total_chat_messages > 0:
                participation_pct = round((message_count / total_chat_messages) * 100, 1)

            # Check if user is admin
            is_user_admin = await is_admin(client, event.chat_id, target_user_id)
            admin_status = "Админ 👑" if is_user_admin else "Пользователь"

            # Format statistics
            user_name = user.first_name
            if hasattr(user, 'last_name') and user.last_name:
                user_name += f" {user.last_name}"
                
            stats = f"**📊 Статистика пользователя {user_name}**"
            if hasattr(user, 'username') and user.username:
                stats += f" (@{user.username})"
            stats += "\n\n"
            
            period_text = f"за последние {days} {'день' if days == 1 else 'дня' if 1 < days < 5 else 'дней'}"
            stats += f"**Период:** {period_text}\n"
            stats += f"**Статус:** {admin_status}\n"
            stats += f"**Сообщений:** {message_count}\n"
            
            if total_chat_messages > 0:
                stats += f"**Активность в чате:** {participation_pct}%\n"
                
            stats += f"**Медиа сообщений:** {media_count}" 
            if message_count > 0:
                stats += f" ({round(media_count/message_count*100, 1)}%)"
            stats += "\n"
            
            stats += f"**Получено ответов:** {reply_count}\n"
            stats += f"**Активность по времени:** {active_hours_str}\n"
            
            if hasattr(user, 'date') and user.date:
                stats += f"**Дата регистрации:** {user.date.strftime('%Y-%m-%d')}\n"
            
            # Add top message types if available
            if message_types and message_count > 0:
                stats += "\n**Типы сообщений:**\n"
                for msg_type, count in message_types.most_common(3):
                    stats += f"• {msg_type}: {count} ({round(count/message_count*100, 1)}%)\n"

            await event.edit(stats)
        except Exception as e:
            logger.error(f"Error in user_stats: {e}", exc_info=True)
            await event.edit(f"Не удалось получить статистику пользователя: {str(e)}")
