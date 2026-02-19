import asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession

API_ID = 37531198
API_HASH = "d4b3a4ee64a1e2d2981e6ebb943e518d"

async def main():
    async with TelegramClient(StringSession(), API_ID, API_HASH) as client:
        # Первый раз спросит номер и код
        print("STRING_SESSION=" + client.session.save())

if __name__ == "__main__":
    asyncio.run(main())
