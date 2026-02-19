import os
import asyncio
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

from telethon import TelegramClient
from telethon.sessions import StringSession

API_ID = int(os.environ["TG_API_ID"])
API_HASH = os.environ["TG_API_HASH"]
SESSION = os.environ["TG_STRING_SESSION"]
BOT = os.getenv("BOT_USERNAME", "hh_rabota_bot")

BASE_DIR = Path(__file__).resolve().parent
LOG_PATH = BASE_DIR / "raise_cv.log"


def log(msg: str) -> None:
    ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    line = f"[{ts}] {msg}"
    print(line)
    LOG_PATH.open("a", encoding="utf-8").write(line + "\n")


async def notify(client: TelegramClient, text: str) -> None:
    try:
        await client.send_message("me", text)  # Saved Messages
    except Exception as e:
        log(f"NOTIFY_ERROR: {type(e).__name__}: {e}")


def find_button(msg, contains: str):
    buttons = getattr(msg, "buttons", None)
    if not buttons:
        return None
    needle = contains.casefold()
    for row in buttons:
        for btn in row:
            text = (btn.text or "").casefold()
            if needle in text:
                return btn
    return None


def extract_time(text: str) -> Optional[str]:
    m = re.search(r"\b(\d{1,2}:\d{2})\b", text or "")
    return m.group(1) if m else None


def is_too_early(text: str) -> bool:
    low = (text or "").casefold()
    return "пока рано" in low or "не прошло 4 часа" in low


async def run_flow() -> int:
    client = TelegramClient(StringSession(SESSION), API_ID, API_HASH)
    await client.connect()

    if not await client.is_user_authorized():
        log("FATAL: session not authorized")
        await client.disconnect()
        return 20

    try:
        try:
            async with client.conversation(BOT, timeout=30) as conv:
                log("[1] /start")
                await conv.send_message("/start")
                start_msg = await conv.get_response()
                log(f"START: {start_msg.text}")

                lk_btn = find_button(start_msg, "Личный кабинет")
                if not lk_btn:
                    log("ERROR: No 'Личный кабинет' button")
                    await notify(client, "❌ RaiseCV: не найдена кнопка 'Личный кабинет'")
                    return 2

                await lk_btn.click()
                lk_msg = await conv.get_response()
                log(f"LK: {lk_msg.text}")

                up_btn = find_button(lk_msg, "Поднять резюме")
                if not up_btn:
                    log("ERROR: No 'Поднять резюме' button")
                    await notify(client, "❌ RaiseCV: не найдена кнопка 'Поднять резюме'")
                    return 3

                await up_btn.click()
                resp = await conv.get_response()
                text = resp.text or ""
                log(f"UP_SEARCH: {text}")

                confirm_btn = find_button(resp, "Поднять")
                if confirm_btn:
                    await confirm_btn.click()
                    final_msg = await conv.get_response()
                    log(f"FINAL: {final_msg.text}")
                    await notify(client, "✅ RaiseCV: действие подтверждено/выполнено")
                    return 0

                if is_too_early(text):
                    when = extract_time(text)
                    status = f"TOO_EARLY_SCHEDULED_{when or '??:??'}"
                    log(f"STATUS: {status}")
                    await notify(client, f"✅ RaiseCV: {status}")
                    return 0

                log("STATUS: UNKNOWN_STATE")
                await notify(client, "⚠️ RaiseCV: UNKNOWN_STATE (проверь лог)")
                return 5

        except Exception as e:
            log(f"FATAL: {type(e).__name__}: {e}")
            await notify(client, f"❌ RaiseCV ERROR: {type(e).__name__}: {e}")
            return 10

    finally:
        await client.disconnect()


def main() -> int:
    return asyncio.run(run_flow())


if __name__ == "__main__":
    sys.exit(main())
