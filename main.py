import os
import asyncio
import random
import threading
from flask import Flask
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.exceptions import TelegramRetryAfter

# ==========================================
# 1. Flask Web Server Setup (Render Web Service ke liye)
# ==========================================
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running successfully on Render!"

def run_flask():
    # Render automatically PORT environment variable assign karta hai
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)


# ==========================================
# 2. Telegram Bot Setup & Animations
# ==========================================
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable is not set! Kripya Render par BOT_TOKEN add karein.")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Saari categories ke emojis ka collection
ALL_EMOJI_CATEGORIES = {
    "Smileys & Emotion": ["😀", "😃", "😄", "😁", "😆", "😅", "😂", "🤣", "🥹", "😊", "😇", "🙂", "😉", "😍", "🥰", "😘", "😜", "🤩", "🥳", "😎", "🤯", "🥵", "🥶", "😱", "🔥", "✨"],
    "Hand Gestures & People": ["👍", "👎", "👌", "✌️", "🤞", "🤟", "🤘", "🤙", "👈", "👉", "👆", "👇", "👏", "🙌", "👐", "🤝", "🙏", "💪", "🫡", "🙋‍♂️", "👑"],
    "Animals & Nature": ["🐶", "🐱", "🐭", "🐹", "🐰", "🦊", "🐻", "🐼", "🐨", "🐯", "🦁", "🐮", "🐷", "🐸", "🐵", "🐔", "🐧", "🦅", "🦉", "🐺", "🦄", "🐝", "🦋"],
    "Food & Drink": ["🍏", "🍎", "🍐", "🍊", "🍋", "🍌", "🍉", "🍇", "🍓", "🫐", "🍒", "🍑", "🥭", "🍍", "🥥", "🥝", "🍅", "🥑", "🍔", "🍟", "🍕", "🌭", "🍿", "🍩", "🍪"],
    "Activities & Sports": ["⚽", "🏀", "🏈", "⚾", "🥎", "🎾", "🏐", "🏉", "🥏", "🎱", "🪀", "🏓", "🏸", "🏒", "🥊", "🥋", "🎯", "⛳", "🎮", "🎲"],
    "Travel & Places": ["🚗", "🚕", "🚙", "🚌", "🚎", "🏎️", "🚓", "🚑", "🚒", "🚐", "🛻", "🚚", "🚛", "🚜", "🛵", "🏍️", "🛺", "🚲", "✈️", "🚀", "🛸", "🚁", "⛵", "🚢"],
    "Objects & Items": ["⌚", "📱", "📲", "💻", "⌨️", "🖥️", "🖨️", "🕹️", "💽", "💾", "💿", "📀", "📷", "📸", "📹", "🎥", "📽️", "💡", "🔦", "💎", "🔮", "🪄", "💣", "🎁"],
    "Symbols & Hearts": ["❤️", "🧡", "💛", "💚", "💙", "💜", "🖤", "🤍", "🤎", "💔", "❤️‍🔥", "💯", "💢", "💥", "💫", "💦", "💨", "🛑", "⛔", "⭕", "❌", "❓", "❗", "⚠️"]
}

# Sabhi categories ke emojis ko ek single list me combine karna
FULL_EMOJI_POOL = [emoji for group in ALL_EMOJI_CATEGORIES.values() for emoji in group]


# Command 1: /rocket (Apni jagah rocket animation)
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
            await asyncio.sleep(e.retry_after)
            await msg.edit_text(frame)
        except Exception:
            pass


# Command 2: /big (Bada random emoji animation - Static in-place replace)
@dp.message(Command("big"))
async def cmd_big_animation(message: types.Message):
    msg = await message.answer("🌀 Initializing Big Emoji Matrix...")
    await asyncio.sleep(0.4)

    total_frames = 15
    
    for i in range(total_frames):
        # 9 random emojis select karna ek 3x3 grid ke liye
        selected_emojis = random.sample(FULL_EMOJI_POOL, 9)
        
        frame_text = (
            f"{selected_emojis[0]}  {selected_emojis[1]}  {selected_emojis[2]}\n"
            f"{selected_emojis[3]}  {selected_emojis[4]}  {selected_emojis[5]}\n"
            f"{selected_emojis[6]}  {selected_emojis[7]}  {selected_emojis[8]}"
        )
        
        try:
            await msg.edit_text(frame_text)
            await asyncio.sleep(0.35)
        except TelegramRetryAfter as e:
            await asyncio.sleep(e.retry_after)
        except Exception:
            pass

    # Animation khatam hone par final message
    final_emojis = random.sample(FULL_EMOJI_POOL, 3)
    await msg.edit_text(f"✨ Animation Complete! ✨\n\n{' '.join(final_emojis)}")


# ==========================================
# 3. Main Runner (Flask Thread + Bot Polling)
# ==========================================
async def main():
    # Flask server ko alag thread me start karna taaki bot ka polling block na ho
    threading.Thread(target=run_flask, daemon=True).start()
    
    print("Bot and Flask server are starting...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
    
