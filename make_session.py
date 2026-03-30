import asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession

API_ID = 0
API_HASH = "PUT_YOUR_API_HASH_HERE"

async def main():
    async with TelegramClient(StringSession(), API_ID, API_HASH) as client:
        # Первый раз спросит номер и код
        print("STRING_SESSION=" + client.session.save())

if __name__ == "__main__":
    asyncio.run(main())
