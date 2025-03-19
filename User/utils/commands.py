"""Модуль с общими командами для Telegram UserBot"""
import asyncio
import logging
from telethon import TelegramClient, events
from telethon.tl.types import ChannelParticipantsAdmins
import config
from utils.helpers import is_admin, cleanup_message

logger = logging.getLogger(__name__)

def register_handlers(client: TelegramClient):
    """Register utility command handlers"""
    
    @client.on(events.NewMessage(pattern=f"\\{config.CMD_PREFIX}all"))
    async def mention_all(event):
        """Command to mention all users in chat"""
        try:
            if not event.is_group:
                await event.reply("❌ Эта команда работает только в группах")
                return
                
            # Проверяем права администратора
            if not await is_admin(client, event.chat_id, event.sender_id):
                await event.reply("🚫 Эта команда только для администраторов")
                await cleanup_message(client, event.message, 5)
                return
                
            # Получаем текст сообщения без команды
            message_text = event.message.text.split(f"{config.CMD_PREFIX}all", 1)
            if len(message_text) > 1:
                text = message_text[1].strip()
            else:
                text = "Внимание всем!"
                
            chat = await event.get_input_chat()
            
            # Отправляем сообщение о начале процесса
            progress_msg = await event.reply("⏳ Собираю список участников...")
            
            # Получаем список участников
            all_participants = []
            async for participant in client.iter_participants(chat):
                if not participant.bot and not participant.deleted:
                    all_participants.append(participant)
            
            # Обновляем сообщение о прогрессе
            await progress_msg.edit("⏳ Формирую упоминания...")
            
            # Формируем упоминания с разбивкой на части
            mentions = []
            chunk_size = 5  # Количество упоминаний в одном сообщении
            for i in range(0, len(all_participants), chunk_size):
                chunk = all_participants[i:i+chunk_size]
                mention_text = f"{text}\n\n"
                for user in chunk:
                    if user.username:
                        mention_text += f"@{user.username} "
                    else:
                        mention_text += f"[{user.first_name}](tg://user?id={user.id}) "
                mentions.append(mention_text)
            
            # Удаляем исходное сообщение с командой
            await event.delete()
            
            # Удаляем сообщение о прогрессе
            await progress_msg.delete()
            
            # Отправляем упоминания
            for mention in mentions:
                await client.send_message(event.chat_id, mention, parse_mode='md')
                # Делаем небольшую паузу между сообщениями
                await asyncio.sleep(1)
                
            logger.info(f"Команда all выполнена в чате {event.chat_id}, упомянуто {len(all_participants)} пользователей")
        except Exception as e:
            logger.error(f"Ошибка при выполнении команды all: {e}")
            await event.reply(f"❌ Произошла ошибка: {str(e)}")