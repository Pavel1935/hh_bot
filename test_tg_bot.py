import pytest
import pytest_asyncio
from telethon import TelegramClient

API_ID = 37531198
API_HASH = "d4b3a4ee64a1e2d2981e6ebb943e518d"
SESSION_NAME = "hh_test"
BOT = "hh_rabota_bot"


def find_button(msg, contains: str):
    if not getattr(msg, "buttons", None):
        return None
    for row in msg.buttons:
        for btn in row:
            if contains in (btn.text or ""):
                return btn
    return None


@pytest_asyncio.fixture()
async def tg_client():
    client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
    await client.start()
    yield client
    await client.disconnect()


@pytest.mark.asyncio
async def test_raise_cv_flow(tg_client):
    async with tg_client.conversation(BOT, timeout=20) as conv:
        # 1) /start
        await conv.send_message("/start")
        start_msg = await conv.get_response()
        print("START:", start_msg.text)

        # 2) Личный кабинет
        lk_btn = find_button(start_msg, "Личный кабинет")
        assert lk_btn, "Кнопка 'Личный кабинет' не найдена"
        await lk_btn.click()
        lk_msg = await conv.get_response()
        print("LK:", lk_msg.text)

        # 3) Поднять резюме в поиске
        up_search_btn = find_button(lk_msg, "Поднять резюме")
        assert up_search_btn, "Кнопка 'Поднять резюме' не найдена"
        await up_search_btn.click()
        up_search_msg = await conv.get_response()
        print("UP SEARCH:", up_search_msg.text)

        # 4) Поднять
        up_btn = find_button(up_search_msg, "Поднять")
        assert up_btn, "Кнопка 'Поднять' не найдена"
        await up_btn.click()
        final_msg = await conv.get_response()
        print("FINAL:", final_msg.text)

        assert (final_msg.text or "").strip() != ""
