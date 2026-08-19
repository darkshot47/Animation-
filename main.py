import os
import asyncio
import random
import threading
import aiohttp

from flask import Flask
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.exceptions import TelegramRetryAfter, TelegramBadRequest


# ==========================================
# 1. Flask Web Server Setup (Render ke liye)
# ==========================================

app = Flask(__name__)


@app.route('/')
def home():
    return "Bot is running successfully on Render with Infinite Animation!"


def run_flask():
    port = int(os.environ.get("PORT", 8000))

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False,
        use_reloader=False
    )


# ==========================================
# 2. Telegram Bot Setup
# ==========================================

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError(
        "BOT_TOKEN environment variable is not set! "
        "Kripya Render par BOT_TOKEN add karein."
    )


bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


# ==========================================
# 3. Render Keep-Alive
# ==========================================

RENDER_URL = "https://animation-0wko.onrender.com/"


async def keep_alive():
    """
    Har 1 minute par Render URL ko ping karega.
    """

    timeout = aiohttp.ClientTimeout(total=15)

    async with aiohttp.ClientSession(
        timeout=timeout
    ) as session:

        while True:

            try:
                async with session.get(
                    RENDER_URL
                ) as response:

                    print(
                        f"[KEEP-ALIVE] "
                        f"Ping: {response.status}"
                    )

            except Exception as e:

                print(
                    f"[KEEP-ALIVE] "
                    f"Error: {e}"
                )

            await asyncio.sleep(60)


# ==========================================
# 4. MASSIVE Emoji Collection Generation
# ==========================================

FULL_EMOJI_POOL = []

emoji_ranges = [
    (0x1F600, 0x1F64F),  # Smileys & Emotion
    (0x1F300, 0x1F5FF),  # Misc Symbols and Pictographs
    (0x1F680, 0x1F6FF),  # Transport and Map
    (0x1F900, 0x1F9FF),  # Supplemental Symbols
    (0x1FA70, 0x1FAFF),  # Extended Symbols
    (0x2600, 0x26FF),    # Miscellaneous Symbols
    (0x2700, 0x27BF),    # Dingbats
]


for start, end in emoji_ranges:

    for i in range(start, end + 1):

        FULL_EMOJI_POOL.append(
            chr(i)
        )


# ==========================================
# 5. Commands & Animations
# ==========================================

# ==========================================
# Command 1: /rocket
# ==========================================

@dp.message(Command("rocket"))
async def cmd_rocket(message: types.Message):

    frames = [
        "🔴 Countdown: 3...",
        "🟡 Countdown: 2...",
        "🟢 Countdown: 1...",
        "🚀 Ignition!",
        "🚀💨 Blast Off!",
        "✨🚀 Star Travelling...",
        "🌕 Landing on Moon!",
        "🎉 Mission Accomplished! 🛰️"
    ]

    msg = await message.answer(frames[0])

    for frame in frames[1:]:

        await asyncio.sleep(0.6)

        try:

            await msg.edit_text(frame)

        except TelegramRetryAfter as e:

            await asyncio.sleep(
                e.retry_after
            )

            await msg.edit_text(frame)

        except Exception:

            pass


# ==========================================
# Command 2: /big
# BINA RUKE chalne wala Infinite Animation
# ==========================================

@dp.message(Command("big"))
async def cmd_big_animation(
    message: types.Message
):

    msg = await message.answer(
        "🌀 Opening Infinite Emoji Matrix..."
    )

    await asyncio.sleep(0.5)

    # Infinite animation
    while True:

        # 3000+ emojis me se 9 random
        selected_emojis = random.sample(
            FULL_EMOJI_POOL,
            9
        )

        frame_text = (
            f"{selected_emojis[0]}  "
            f"{selected_emojis[1]}  "
            f"{selected_emojis[2]}\n\n"

            f"{selected_emojis[3]}  "
            f"{selected_emojis[4]}  "
            f"{selected_emojis[5]}\n\n"

            f"{selected_emojis[6]}  "
            f"{selected_emojis[7]}  "
            f"{selected_emojis[8]}"
        )

        try:

            await msg.edit_text(
                frame_text
            )

            # 0.8 second delay
            await asyncio.sleep(0.8)

        except TelegramRetryAfter as e:

            await asyncio.sleep(
                e.retry_after
            )

        except TelegramBadRequest as e:

            if (
                "message to edit not found"
                in str(e).lower()
                or
                "message is not modified"
                in str(e).lower()
            ):
                break

        except Exception:

            await asyncio.sleep(1)


# ==========================================
# 6. Main Runner
# ==========================================

async def main():

    # Flask server ko alag thread me chalana
    threading.Thread(
        target=run_flask,
        daemon=True
    ).start()

    # Keep-alive background task
    asyncio.create_task(
        keep_alive()
    )

    print(
        "Bot and Flask server are starting..."
    )

    print(
        "Render keep-alive started "
        "(60 seconds interval)"
    )

    # Telegram bot start
    await dp.start_polling(bot)


# ==========================================
# 7. Start
# ==========================================

if __name__ == "__main__":
    asyncio.run(main())
