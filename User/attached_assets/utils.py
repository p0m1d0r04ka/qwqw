from telethon import TelegramClient, events
from telethon.tl.types import ChannelParticipantsAdmins
import config
import logging
from utils.helpers import is_admin, cleanup_message

logger = logging.getLogger(__name__)

def register_handlers(client: TelegramClient):
    @client.on(events.NewMessage(pattern=f"\\{config.CMD_PREFIX}mention_all"))
    async def mention_all(event):
        try:
            # Check if sender is admin
            if not await is_admin(event.client, event.chat_id, event.sender_id):
                await event.edit("Эта команда доступна только админам!")
                if config.CLEANUP_ENABLED:
                    await cleanup_message(event.client, event.message, config.CLEANUP_DELAY)
                return

            logger.info(f"Mentioning all users in chat {event.chat_id}")
            await event.edit("Упоминание всех участников чата...")

            # Get all participants
            participants = []
            async for user in event.client.iter_participants(event.chat_id):
                if user.bot:
                    continue
                if user.username:
                    participants.append(f"@{user.username}")
                else:
                    participants.append(f"[{user.first_name}](tg://user?id={user.id})")

            # Split mentions into chunks to avoid message length limits
            chunk_size = 7  # Adjusted for better display
            mention_chunks = [participants[i:i + chunk_size] 
                            for i in range(0, len(participants), chunk_size)]

            # Delete original command
            await event.delete()

            # Send mentions as new messages
            for chunk in mention_chunks:
                await event.respond(" ".join(chunk))
                
            logger.info(f"Mentioned {len(participants)} users in {len(mention_chunks)} messages")

        except Exception as e:
            logger.error(f"Error in mention_all: {e}")
            await event.edit(f"Не удалось упомянуть всех пользователей: {str(e)}")
