from telethon import TelegramClient, events
from telethon.tl.functions.channels import EditBannedRequest
from telethon.tl.types import ChatBannedRights
from datetime import datetime, timedelta
import config
from utils.helpers import is_admin, check_user_is_not_admin, cleanup_message, get_current_warnings, add_warning, clear_warnings
import logging
import asyncio

logger = logging.getLogger(__name__)

def register_handlers(client: TelegramClient):
    @client.on(events.NewMessage(pattern=f"\\{config.CMD_PREFIX}warn"))
    async def warn_user(event):
        try:
            # Check if sender is admin
            if not await is_admin(event.client, event.chat_id, event.sender_id):
                await event.edit("Эта команда доступна только админам!")
                if config.CLEANUP_ENABLED:
                    await cleanup_message(event.client, event.message, config.CLEANUP_DELAY)
                return

            if not event.reply_to_msg_id:
                await event.edit("Ответьте на сообщение пользователя, которому хотите выдать предупреждение!")
                if config.CLEANUP_ENABLED:
                    await cleanup_message(event.client, event.message, config.CLEANUP_DELAY)
                return

            replied_msg = await event.get_reply_message()
            target_user_id = replied_msg.sender_id
            
            # Ensure target user is not an admin
            if not await check_user_is_not_admin(event.client, event.chat_id, target_user_id):
                await event.edit("Невозможно дать предупреждение администратору!")
                if config.CLEANUP_ENABLED:
                    await cleanup_message(event.client, event.message, config.CLEANUP_DELAY)
                return
            
            # Get user info
            target_user = await event.client.get_entity(target_user_id)
            target_name = target_user.first_name
            if hasattr(target_user, 'username') and target_user.username:
                target_name += f" (@{target_user.username})"
            
            # Add warning and get current count
            warning_count = add_warning(event.chat_id, target_user_id, config.WARNINGS)
            
            # Check if user needs to be banned
            if warning_count >= config.MAX_WARNINGS:
                # Ban user (стандартный набор для бана через предупреждения)
                rights = ChatBannedRights(
                    until_date=None,  # Бан навсегда
                    view_messages=True,  # Запрет просмотра сообщений (исключение из группы)
                    send_messages=True,
                    send_media=True,
                    send_stickers=True,
                    send_gifs=True,
                    send_games=True,
                    send_inline=True,
                    embed_links=True,
                    pin_messages=True,
                    invite_users=True,
                    change_info=True
                )

                await event.client(EditBannedRequest(
                    event.chat_id,
                    target_user_id,
                    rights
                ))
                
                # Clear warnings after ban
                clear_warnings(event.chat_id, target_user_id, config.WARNINGS)
                
                await event.edit(f"Пользователь {target_name} получил {warning_count}/{config.MAX_WARNINGS} предупреждений и был забанен!")
            else:
                # Just warn
                await event.edit(f"Пользователь {target_name} получил предупреждение ({warning_count}/{config.MAX_WARNINGS}).")
            
            # Schedule cleanup of command message
            if config.CLEANUP_ENABLED:
                await cleanup_message(event.client, event.message, config.CLEANUP_DELAY * 2)
                
        except Exception as e:
            logger.error(f"Error in warn_user: {e}")
            await event.edit(f"Не удалось выдать предупреждение: {str(e)}")

    @client.on(events.NewMessage(pattern=f"\\{config.CMD_PREFIX}tmute"))
    async def tmute_user(event):
        try:
            # Check if sender is admin
            if not await is_admin(event.client, event.chat_id, event.sender_id):
                await event.edit("Эта команда доступна только админам!")
                if config.CLEANUP_ENABLED:
                    await cleanup_message(event.client, event.message, config.CLEANUP_DELAY)
                return

            if not event.reply_to_msg_id:
                await event.edit("Ответьте на сообщение пользователя, которого хотите временно заглушить!")
                if config.CLEANUP_ENABLED:
                    await cleanup_message(event.client, event.message, config.CLEANUP_DELAY)
                return

            # Parse arguments
            args = event.text.split()
            mute_minutes = config.DEFAULT_MUTE_DURATION
            
            if len(args) > 1:
                try:
                    mute_minutes = int(args[1])
                    if mute_minutes <= 0:
                        raise ValueError()
                except ValueError:
                    await event.edit(f"Неверный формат времени. Использование: `{config.CMD_PREFIX}tmute <минуты>`")
                    if config.CLEANUP_ENABLED:
                        await cleanup_message(event.client, event.message, config.CLEANUP_DELAY)
                    return

            replied_msg = await event.get_reply_message()
            target_user_id = replied_msg.sender_id
            
            # Ensure target user is not an admin
            if not await check_user_is_not_admin(event.client, event.chat_id, target_user_id):
                await event.edit("Невозможно заглушить администратора!")
                if config.CLEANUP_ENABLED:
                    await cleanup_message(event.client, event.message, config.CLEANUP_DELAY)
                return
            
            # Get user info
            target_user = await event.client.get_entity(target_user_id)
            target_name = target_user.first_name
            if hasattr(target_user, 'username') and target_user.username:
                target_name += f" (@{target_user.username})"
            
            # Calculate unmute time
            mute_until = datetime.now() + timedelta(minutes=mute_minutes)
            
            # Define temporary mute rights (стандартный набор для временного мута)
            rights = ChatBannedRights(
                until_date=mute_until,  # Мут на указанное время
                send_messages=True,  # Запрет отправки текстовых сообщений
                send_media=True,  # Запрет отправки медиа
                send_stickers=True,  # Запрет стикеров
                send_gifs=True,  # Запрет гифок
                send_games=True,  # Запрет игр
                send_inline=True,  # Запрет инлайн-ботов
                embed_links=True,  # Запрет встраивания ссылок
                # Важно: view_messages=False, так как это не бан, а временный мут
                view_messages=False  # Пользователь может видеть сообщения
            )

            # Apply temporary mute
            await event.client(EditBannedRequest(
                event.chat_id,
                target_user_id,
                rights
            ))

            # Format with human-readable time
            unmute_time = mute_until.strftime("%H:%M:%S %d.%m.%Y")
            await event.edit(f"Пользователь {target_name} заглушен на {mute_minutes} минут (до {unmute_time}).")
            
            # Schedule cleanup of command message
            if config.CLEANUP_ENABLED:
                await cleanup_message(event.client, event.message, config.CLEANUP_DELAY * 2)
                
        except Exception as e:
            logger.error(f"Error in tmute_user: {e}")
            await event.edit(f"Не удалось временно заглушить пользователя: {str(e)}")
