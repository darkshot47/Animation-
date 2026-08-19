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
# 1. Flask Web Server Setup
# ==========================================

app = Flask(__name__)


@app.route("/")
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
    Har 60 seconds mein Render URL ko request karega.
    """

    timeout = aiohttp.ClientTimeout(total=20)

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
                        f"Status: {response.status}"
                    )

            except asyncio.CancelledError:
                print("[KEEP-ALIVE] Task cancelled.")
                raise

            except Exception as e:

                print(
                    f"[KEEP-ALIVE] "
                    f"Error: {repr(e)}"
                )

            # 60 seconds wait
            await asyncio.sleep(60)


# ==========================================
# 4. Massive Emoji Collection
# ==========================================

FULL_EMOJI_POOL = []


emoji_ranges = [
    (0x1F600, 0x1F64F),  # Smileys & Emotion
    (0x1F300, 0x1F5FF),  # Misc Symbols
    (0x1F680, 0x1F6FF),  # Transport
    (0x1F900, 0x1F9FF),  # Supplemental
    (0x1FA70, 0x1FAFF),  # Extended
    (0x2600, 0x26FF),    # Misc Symbols
    (0x2700, 0x27BF),    # Dingbats
]


for start, end in emoji_ranges:

    for codepoint in range(
        start,
        end + 1
    ):

        FULL_EMOJI_POOL.append(
            chr(codepoint)
        )


print(
    f"Emoji pool loaded: "
    f"{len(FULL_EMOJI_POOL)} characters"
)


# ==========================================
# 5. /rocket Command
# ==========================================

@dp.message(Command("rocket"))
async def cmd_rocket(
    message: types.Message
):

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

    try:

        msg = await message.answer(
            frames[0]
        )

        for frame in frames[1:]:

            await asyncio.sleep(0.6)

            while True:

                try:

                    await msg.edit_text(
                        frame
                    )

                    break

                except TelegramRetryAfter as e:

                    print(
                        f"[ROCKET] "
                        f"Rate limit: "
                        f"{e.retry_after}s"
                    )

                    await asyncio.sleep(
                        e.retry_after
                    )

                except TelegramBadRequest as e:

                    error = str(e).lower()

                    print(
                        f"[ROCKET] "
                        f"Telegram error: "
                        f"{error}"
                    )

                    if (
                        "message to edit not found"
                        in error
                        or
                        "message can't be edited"
                        in error
                    ):
                        return

                    # Dusre Telegram errors par
                    # thoda wait karke next frame
                    break

                except Exception as e:

                    print(
                        f"[ROCKET] "
                        f"Unexpected error: "
                        f"{repr(e)}"
                    )

                    break

    except Exception as e:

        print(
            f"[ROCKET] "
            f"Command error: "
            f"{repr(e)}"
        )


# ==========================================
# 6. /big Command
# Infinite Emoji Animation
# ==========================================

@dp.message(Command("big"))
async def cmd_big_animation(
    message: types.Message
):

    try:

        msg = await message.answer(
            "🌀 Opening Infinite Emoji Matrix..."
        )

        await asyncio.sleep(0.5)

        while True:

            # 9 random emojis
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

                print(
                    "[BIG] Frame updated"
                )

                # Animation speed
                await asyncio.sleep(0.8)

            except TelegramRetryAfter as e:

                print(
                    f"[BIG] "
                    f"Rate limit: "
                    f"{e.retry_after}s"
                )

                await asyncio.sleep(
                    e.retry_after
                )

            except TelegramBadRequest as e:

                error = str(e).lower()

                print(
                    f"[BIG] "
                    f"Telegram error: "
                    f"{error}"
                )

                # User ne message delete kar diya
                if (
                    "message to edit not found"
                    in error
                    or
                    "message can't be edited"
                    in error
                ):
                    print(
                        "[BIG] "
                        "Message no longer editable."
                    )

                    break

                # Same content wala error
                if "message is not modified" in error:

                    await asyncio.sleep(
                        0.8
                    )

                    continue

                await asyncio.sleep(1)

            except Exception as e:

                print(
                    f"[BIG] "
                    f"Unexpected error: "
                    f"{repr(e)}"
                )

                await asyncio.sleep(1)

    except Exception as e:

        print(
            f"[BIG] "
            f"Command error: "
            f"{repr(e)}"
        )


# ==========================================
# 7. Main Runner
# ==========================================

async def main():

    print(
        "===================================="
    )

    print(
        "Starting Flask server..."
    )

    flask_thread = threading.Thread(
        target=run_flask,
        daemon=True
    )

    flask_thread.start()

    print(
        "Starting Render keep-alive..."
    )

    keep_alive_task = asyncio.create_task(
        keep_alive()
    )

    print(
        "Starting Telegram bot..."
    )

    print(
        "===================================="
    )

    try:

        await dp.start_polling(
            bot
        )

    finally:

        print(
            "Stopping keep-alive..."
        )

        keep_alive_task.cancel()

        try:
            await keep_alive_task
        except asyncio.CancelledError:
            pass

        await bot.session.close()


# ==========================================
# 8. Start Application
# ==========================================

if __name__ == "__main__":

    try:

        asyncio.run(
            main()
        )

    except KeyboardInterrupt:

        print(
            "Bot stopped manually."
    )
