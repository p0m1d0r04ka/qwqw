from telethon import TelegramClient, events
from telethon.tl.functions.channels import DeleteMessagesRequest, EditBannedRequest
from telethon.tl.types import ChatBannedRights
from datetime import timedelta
import config
from utils.helpers import is_admin, check_user_is_not_admin, cleanup_message
import logging

logger = logging.getLogger(__name__)

def register_handlers(client: TelegramClient):
    @client.on(events.NewMessage(pattern=f"\\{config.CMD_PREFIX}clear_all"))
    async def clear_all(event):
        try:
            # Check if sender is admin
            if not await is_admin(event.client, event.chat_id, event.sender_id):
                await event.edit("Эта команда доступна только админам!")
                if config.CLEANUP_ENABLED:
                    await cleanup_message(event.client, event.message, config.CLEANUP_DELAY)
                return

            await event.edit("Очистка чата...")

            # Delete all messages in chat
            delete_count = 0
            async for message in event.client.iter_messages(event.chat_id):
                await message.delete()
                delete_count += 1
                # Add a small delay to avoid hitting rate limits
                if delete_count % 50 == 0:
                    await event.edit(f"Удалено {delete_count} сообщений...")

            await event.respond("Чат успешно очищен!")
        except Exception as e:
            logger.error(f"Error in clear_all: {e}")
            await event.edit(f"Не удалось очистить сообщения в чате: {str(e)}")

    @client.on(events.NewMessage(pattern=f"\\{config.CMD_PREFIX}clear_user"))
    async def clear_user(event):
        try:
            # Check if sender is admin
            if not await is_admin(event.client, event.chat_id, event.sender_id):
                await event.edit("Эта команда доступна только админам!")
                if config.CLEANUP_ENABLED:
                    await cleanup_message(event.client, event.message, config.CLEANUP_DELAY)
                return

            if not event.reply_to_msg_id:
                await event.edit("Ответьте на сообщение пользователя, чьи сообщения нужно удалить!")
                if config.CLEANUP_ENABLED:
                    await cleanup_message(event.client, event.message, config.CLEANUP_DELAY)
                return

            replied_msg = await event.get_reply_message()
            target_user = replied_msg.sender_id
            
            # Get user info for the log
            target_user_obj = await event.client.get_entity(target_user)
            target_name = target_user_obj.first_name
            if hasattr(target_user_obj, 'username') and target_user_obj.username:
                target_name += f" (@{target_user_obj.username})"
                
            logger.info(f"Clearing messages from user {target_name} in chat {event.chat_id}")

            await event.edit(f"Удаление сообщений пользователя {target_name}...")

            # Delete messages from target user
            delete_count = 0
            async for message in event.client.iter_messages(
                event.chat_id,
                from_user=target_user
            ):
                await message.delete()
                delete_count += 1
                # Add a small delay to avoid hitting rate limits
                if delete_count % 20 == 0:
                    await event.edit(f"Удалено {delete_count} сообщений...")

            await event.edit(f"Удалено {delete_count} сообщений пользователя {target_name}")
            
            # Schedule cleanup of command message
            if config.CLEANUP_ENABLED:
                await cleanup_message(event.client, event.message, config.CLEANUP_DELAY * 2)
                
        except Exception as e:
            logger.error(f"Error in clear_user: {e}")
            await event.edit(f"Не удалось удалить сообщения пользователя: {str(e)}")

    @client.on(events.NewMessage(pattern=f"\\{config.CMD_PREFIX}ban"))
    async def ban_user(event):
        try:
            # Check if sender is admin
            if not await is_admin(event.client, event.chat_id, event.sender_id):
                await event.edit("Эта команда доступна только админам!")
                if config.CLEANUP_ENABLED:
                    await cleanup_message(event.client, event.message, config.CLEANUP_DELAY)
                return

            if not event.reply_to_msg_id:
                await event.edit("Ответьте на сообщение пользователя, которого хотите забанить!")
                if config.CLEANUP_ENABLED:
                    await cleanup_message(event.client, event.message, config.CLEANUP_DELAY)
                return

            replied_msg = await event.get_reply_message()
            target_user_id = replied_msg.sender_id
            
            # Ensure target user is not an admin
            if not await check_user_is_not_admin(event.client, event.chat_id, target_user_id):
                await event.edit("Невозможно забанить администратора!")
                if config.CLEANUP_ENABLED:
                    await cleanup_message(event.client, event.message, config.CLEANUP_DELAY)
                return
            
            # Get user info for the log
            target_user = await event.client.get_entity(target_user_id)
            target_name = target_user.first_name
            if hasattr(target_user, 'username') and target_user.username:
                target_name += f" (@{target_user.username})"
            
            logger.info(f"Banning user {target_name} from chat {event.chat_id}")
            
            # Define ban rights (стандартный набор для полного бана)
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

            # Apply ban
            await event.client(EditBannedRequest(
                event.chat_id,
                target_user_id,
                rights
            ))

            await event.edit(f"Пользователь {target_name} забанен!")
            
            # Schedule cleanup of command message
            if config.CLEANUP_ENABLED:
                await cleanup_message(event.client, event.message, config.CLEANUP_DELAY * 2)
                
        except Exception as e:
            logger.error(f"Error in ban_user: {e}")
            await event.edit(f"Не удалось забанить пользователя: {str(e)}")

    @client.on(events.NewMessage(pattern=f"\\{config.CMD_PREFIX}mute"))
    async def mute_user(event):
        try:
            # Check if sender is admin
            if not await is_admin(event.client, event.chat_id, event.sender_id):
                await event.edit("Эта команда доступна только админам!")
                if config.CLEANUP_ENABLED:
                    await cleanup_message(event.client, event.message, config.CLEANUP_DELAY)
                return

            if not event.reply_to_msg_id:
                await event.edit("Ответьте на сообщение пользователя, которого хотите заглушить!")
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
            
            # Get user info for the log
            target_user = await event.client.get_entity(target_user_id)
            target_name = target_user.first_name
            if hasattr(target_user, 'username') and target_user.username:
                target_name += f" (@{target_user.username})"
            
            logger.info(f"Muting user {target_name} in chat {event.chat_id}")
            
            # Define mute rights (стандартный набор для заглушения)
            rights = ChatBannedRights(
                until_date=None,  # Мут навсегда
                send_messages=True,  # Запрет отправки текстовых сообщений
                send_media=True,  # Запрет отправки медиа
                send_stickers=True,  # Запрет стикеров
                send_gifs=True,  # Запрет гифок
                send_games=True,  # Запрет игр
                send_inline=True,  # Запрет инлайн-ботов
                embed_links=True,  # Запрет встраивания ссылок
                # Важно: view_messages=False, так как это не бан, а мут
                view_messages=False  # Пользователь может видеть сообщения
            )

            # Apply mute
            await event.client(EditBannedRequest(
                event.chat_id,
                target_user_id,
                rights
            ))

            await event.edit(f"Пользователь {target_name} заглушен!")
            
            # Schedule cleanup of command message
            if config.CLEANUP_ENABLED:
                await cleanup_message(event.client, event.message, config.CLEANUP_DELAY * 2)
                
        except Exception as e:
            logger.error(f"Error in mute_user: {e}")
            await event.edit(f"Не удалось заглушить пользователя: {str(e)}")

    @client.on(events.NewMessage(pattern=f"\\{config.CMD_PREFIX}unmute"))
    async def unmute_user(event):
        try:
            # Check if sender is admin
            if not await is_admin(event.client, event.chat_id, event.sender_id):
                await event.edit("Эта команда доступна только админам!")
                if config.CLEANUP_ENABLED:
                    await cleanup_message(event.client, event.message, config.CLEANUP_DELAY)
                return

            if not event.reply_to_msg_id:
                await event.edit("Ответьте на сообщение пользователя, с которого хотите снять заглушение!")
                if config.CLEANUP_ENABLED:
                    await cleanup_message(event.client, event.message, config.CLEANUP_DELAY)
                return

            replied_msg = await event.get_reply_message()
            target_user_id = replied_msg.sender_id
            
            # Get user info for the log
            target_user = await event.client.get_entity(target_user_id)
            target_name = target_user.first_name
            if hasattr(target_user, 'username') and target_user.username:
                target_name += f" (@{target_user.username})"
            
            logger.info(f"Unmuting user {target_name} in chat {event.chat_id}")
            
            # Define unmute rights (allow all)
            rights = ChatBannedRights(
                until_date=None,
                send_messages=False,
                send_media=False,
                send_stickers=False,
                send_gifs=False,
                send_games=False,
                send_inline=False,
                embed_links=False,
                pin_messages=False,
                invite_users=False,
                change_info=False,
                view_messages=False
            )

            # Apply unmute
            await event.client(EditBannedRequest(
                event.chat_id,
                target_user_id,
                rights
            ))

            await event.edit(f"Заглушение с пользователя {target_name} снято!")
            
            # Schedule cleanup of command message
            if config.CLEANUP_ENABLED:
                await cleanup_message(event.client, event.message, config.CLEANUP_DELAY * 2)
                
        except Exception as e:
            logger.error(f"Error in unmute_user: {e}")
            await event.edit(f"Не удалось снять заглушение с пользователя: {str(e)}")

    @client.on(events.NewMessage(pattern=f"\\{config.CMD_PREFIX}unban"))
    async def unban_user(event):
        try:
            # Check if sender is admin
            if not await is_admin(event.client, event.chat_id, event.sender_id):
                await event.edit("Эта команда доступна только админам!")
                if config.CLEANUP_ENABLED:
                    await cleanup_message(event.client, event.message, config.CLEANUP_DELAY)
                return

            if not event.reply_to_msg_id:
                await event.edit("Ответьте на сообщение пользователя, которого хотите разбанить!")
                if config.CLEANUP_ENABLED:
                    await cleanup_message(event.client, event.message, config.CLEANUP_DELAY)
                return

            replied_msg = await event.get_reply_message()
            target_user_id = replied_msg.sender_id
            
            # Get user info for the log
            target_user = await event.client.get_entity(target_user_id)
            target_name = target_user.first_name
            if hasattr(target_user, 'username') and target_user.username:
                target_name += f" (@{target_user.username})"
            
            logger.info(f"Unbanning user {target_name} from chat {event.chat_id}")
            
            # Define unban rights (снимаем все ограничения)
            rights = ChatBannedRights(
                until_date=None,
                view_messages=False,
                send_messages=False,
                send_media=False,
                send_stickers=False,
                send_gifs=False,
                send_games=False,
                send_inline=False,
                embed_links=False,
                pin_messages=False,
                invite_users=False,
                change_info=False
            )

            # Apply unban
            await event.client(EditBannedRequest(
                event.chat_id,
                target_user_id,
                rights
            ))

            await event.edit(f"Пользователь {target_name} разбанен!")
            
            # Schedule cleanup of command message
            if config.CLEANUP_ENABLED:
                await cleanup_message(event.client, event.message, config.CLEANUP_DELAY * 2)
                
        except Exception as e:
            logger.error(f"Error in unban_user: {e}")
            await event.edit(f"Не удалось разбанить пользователя: {str(e)}")

    @client.on(events.NewMessage(pattern=f"\\{config.CMD_PREFIX}purge"))
    async def purge_messages(event):
        try:
            # Check if sender is admin
            if not await is_admin(event.client, event.chat_id, event.sender_id):
                await event.edit("Эта команда доступна только админам!")
                if config.CLEANUP_ENABLED:
                    await cleanup_message(event.client, event.message, config.CLEANUP_DELAY)
                return
            
            # Parse arguments
            args = event.text.split()
            if len(args) != 2:
                await event.edit("Использование: `/purge <количество>`")
                if config.CLEANUP_ENABLED:
                    await cleanup_message(event.client, event.message, config.CLEANUP_DELAY)
                return
            
            try:
                count = int(args[1])
                if count <= 0:
                    raise ValueError("Count must be positive")
            except ValueError:
                await event.edit("Количество должно быть положительным числом!")
                if config.CLEANUP_ENABLED:
                    await cleanup_message(event.client, event.message, config.CLEANUP_DELAY)
                return
            
            await event.edit(f"Удаление последних {count} сообщений...")
            
            # Delete messages
            deleted = 0
            async for message in event.client.iter_messages(event.chat_id, limit=count+1):  # +1 to include command
                await message.delete()
                deleted += 1
                
                # Provide progress updates for large deletions
                if deleted % 20 == 0 and deleted < count:
                    await event.client.send_message(
                        event.chat_id, 
                        f"Удалено {deleted}/{count} сообщений..."
                    )
            
            # Send completion message
            result = await event.client.send_message(
                event.chat_id, 
                f"Удалено {deleted-1} сообщений!"  # -1 to not count the command itself
            )
            
            # Schedule cleanup of result message
            if config.CLEANUP_ENABLED:
                await cleanup_message(event.client, result, config.CLEANUP_DELAY)
                
        except Exception as e:
            logger.error(f"Error in purge_messages: {e}")
            await event.edit(f"Ошибка при удалении сообщений: {str(e)}")
