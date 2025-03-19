from telethon import TelegramClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API credentials
api_id = os.getenv("API_ID")
api_hash = os.getenv("API_HASH")

print(f"API_ID: {api_id}")
print(f"API_HASH: {api_hash}")

# Create the client and connect
client = TelegramClient('userbot', api_id, api_hash)

async def main():
    await client.start()
    
    # Get information about yourself
    me = await client.get_me()
    print(f"Logged in as {me.first_name} (@{me.username})")
    
    # Send a message to yourself
    await client.send_message('me', 'Hello from Telethon!')
    print("Message sent!")
    
    await client.disconnect()

with client:
    client.loop.run_until_complete(main())