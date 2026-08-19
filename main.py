import os
import asyncio
import random
import threading
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
    app.run(host="0.0.0.0", port=port)


# ==========================================
# 2. Telegram Bot Setup
# ==========================================
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable is not set! Kripya Render par BOT_TOKEN add karein.")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ==========================================
# 3. MASSIVE Emoji Collection Generation (3000+ Emojis)
# ==========================================
FULL_EMOJI_POOL = []
# Unicode hex ranges jahan duniya bhar ke sabhi emojis hote hain
emoji_ranges = [
    (0x1F600, 0x1F64F), # Smileys & Emotion
    (0x1F300, 0x1F5FF), # Misc Symbols and Pictographs (Weather, Food, Animals)
    (0x1F680, 0x1F6FF), # Transport and Map
    (0x1F900, 0x1F9FF), # Supplemental Symbols (New emojis)
    (0x1FA70, 0x1FAFF), # Extended Symbols
    (0x2600, 0x26FF),   # Miscellaneous Symbols
    (0x2700, 0x27BF),   # Dingbats (Stars, Sparkles, etc.)
]

for start, end in emoji_ranges:
    for i in range(start, end + 1):
        FULL_EMOJI_POOL.append(chr(i))


# ==========================================
# 4. Commands & Animations
# ==========================================

# Command 1: /rocket
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


# Command 2: /big (BINA RUKE chalne wala Infinite Animation)
@dp.message(Command("big"))
async def cmd_big_animation(message: types.Message):
    msg = await message.answer("🌀 Opening Infinite Emoji Matrix...")
    await asyncio.sleep(0.5)
    
    # 'while True' ka matlab hai ye loop kabhi khatam nahi hoga (Infinite)
    while True:
        # 3000+ emojis me se koi bhi 9 random uthayega
        selected_emojis = random.sample(FULL_EMOJI_POOL, 9)
        
        frame_text = (
            f"{selected_emojis[0]}  {selected_emojis[1]}  {selected_emojis[2]}\n\n"
            f"{selected_emojis[3]}  {selected_emojis[4]}  {selected_emojis[5]}\n\n"
            f"{selected_emojis[6]}  {selected_emojis[7]}  {selected_emojis[8]}"
        )
        
        try:
            await msg.edit_text(frame_text)
            # 0.8 second ka delay diya hai taaki Telegram bot ko block na kare (Flood limits)
            await asyncio.sleep(0.8)
            
        except TelegramRetryAfter as e:
            # Agar Telegram ko lagta hai bot fast hai, toh bot utne time chup chap wait karega
            await asyncio.sleep(e.retry_after)
            
        except TelegramBadRequest as e:
            # Agar user ne message delete kar diya, toh animation stop ho jayega
            if "message to edit not found" in str(e).lower() or "message is not modified" in str(e).lower():
                break  # Loop yahan tod diya jayega taaki bot crash na ho
                
        except Exception:
            # Kisi bhi chhote mote network issue par bas aage badh jayega
            await asyncio.sleep(1)


# ==========================================
# 5. Main Runner (Flask Thread + Bot)
# ==========================================
async def main():
    # Flask server ko alag thread me chalana
    threading.Thread(target=run_flask, daemon=True).start()
    
    print("Bot and Flask server are starting...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
    
