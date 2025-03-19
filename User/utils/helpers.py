from telethon import TelegramClient
from telethon.tl.types import ChannelParticipantsAdmins
import config
import logging
import asyncio
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Admin cache setup
admin_cache = config.ADMINS_CACHE  # {chat_id: {user_id: expiry_timestamp}}

async def is_admin(client: TelegramClient, chat_id: int, user_id: int) -> bool:
    """Check if user is an admin in the chat with caching"""
    now = datetime.now().timestamp()
    
    # Check cache first
    if chat_id in admin_cache and user_id in admin_cache[chat_id]:
        # If cache entry is still valid
        if admin_cache[chat_id][user_id] > now:
            return True
        # Expired entry
        else:
            del admin_cache[chat_id][user_id]
    
    # Cache miss or expired, check for real
    try:
        chat = await client.get_entity(chat_id)
        async for admin in client.iter_participants(chat, filter=ChannelParticipantsAdmins):
            # Update cache for this admin
            if chat_id not in admin_cache:
                admin_cache[chat_id] = {}
            
            # Set expiry timestamp
            expiry = now + config.ADMIN_CACHE_TTL
            admin_cache[chat_id][admin.id] = expiry
            
            # If this is the user we're checking
            if admin.id == user_id:
                return True
        
        return False
    except Exception as e:
        logger.error(f"Error checking admin status: {e}")
        # In case of error, don't give admin rights
        return False

async def check_user_is_not_admin(client: TelegramClient, chat_id: int, user_id: int) -> bool:
    """Check if user is NOT an admin (for moderation)"""
    is_user_admin = await is_admin(client, chat_id, user_id)
    return not is_user_admin

async def refresh_admin_cache(client: TelegramClient, chat_id: int) -> tuple:
    """Refresh the admin cache for a chat and return stats"""
    logger.info(f"Refreshing admin cache for chat {chat_id}")
    
    # Clear existing cache for this chat
    if chat_id in admin_cache:
        del admin_cache[chat_id]
    else:
        admin_cache[chat_id] = {}
    
    # Fetch all admins
    admin_count = 0
    try:
        chat = await client.get_entity(chat_id)
        now = datetime.now().timestamp()
        expiry = now + config.ADMIN_CACHE_TTL
        
        async for admin in client.iter_participants(chat, filter=ChannelParticipantsAdmins):
            if chat_id not in admin_cache:
                admin_cache[chat_id] = {}
            
            admin_cache[chat_id][admin.id] = expiry
            admin_count += 1
        
        logger.info(f"Admin cache refreshed for chat {chat_id}, found {admin_count} admins")
        return admin_count, True
    except Exception as e:
        logger.error(f"Error refreshing admin cache: {e}")
        return 0, False

async def get_user_count(client: TelegramClient, chat_id: int) -> int:
    """Get the number of users in a chat"""
    try:
        count = 0
        async for _ in client.iter_participants(chat_id):
            count += 1
        return count
    except Exception as e:
        logger.error(f"Error counting users: {e}")
        return 0

async def cleanup_message(client: TelegramClient, message, delay: int = 5):
    """Delete a message after a delay"""
    try:
        await asyncio.sleep(delay)
        await message.delete()
    except Exception as e:
        logger.error(f"Error deleting message: {e}")

def get_current_warnings(chat_id, user_id, warnings_dict):
    """Get current warnings count for a user"""
    chat_str = str(chat_id)
    user_str = str(user_id)
    
    if chat_str not in warnings_dict:
        warnings_dict[chat_str] = {}
    
    if user_str not in warnings_dict[chat_str]:
        warnings_dict[chat_str][user_str] = 0
        
    return warnings_dict[chat_str][user_str]

def add_warning(chat_id, user_id, warnings_dict):
    """Add a warning to a user and return new count"""
    chat_str = str(chat_id)
    user_str = str(user_id)
    
    if chat_str not in warnings_dict:
        warnings_dict[chat_str] = {}
    
    if user_str not in warnings_dict[chat_str]:
        warnings_dict[chat_str][user_str] = 0
    
    warnings_dict[chat_str][user_str] += 1
    return warnings_dict[chat_str][user_str]

def clear_warnings(chat_id, user_id, warnings_dict):
    """Clear all warnings for a user"""
    chat_str = str(chat_id)
    user_str = str(user_id)
    
    if chat_str in warnings_dict and user_str in warnings_dict[chat_str]:
        warnings_dict[chat_str][user_str] = 0