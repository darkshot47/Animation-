import os
import asyncio
import logging
import random
from threading import Thread
from flask import Flask

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import Message

# ==========================================
# 0. LOGGING SETUP
# ==========================================
logging.basicConfig(level=logging.INFO)

# ==========================================
# 1. INITIALIZATION
# ==========================================
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("⚠️ BOT_TOKEN environment variable me set nahi hai!")

PORT = int(os.getenv("PORT", 8080))

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ==========================================
# 2. FLASK KEEP-ALIVE SERVER
# ==========================================
app = Flask(__name__)

@app.route('/')
def home():
    return "Space Bot is running 24/7! 🌌"

def run_server():
    import logging as flask_logging
    flask_log = flask_logging.getLogger('werkzeug')
    flask_log.setLevel(flask_logging.ERROR)
    app.run(host="0.0.0.0", port=PORT)

def keep_alive():
    server_thread = Thread(target=run_server, daemon=True)
    server_thread.start()

# ==========================================
# 3. DYNAMIC SPACE ANIMATION LOGIC
# ==========================================
# Ab hum globally sirf ek active animation track karenge taaki DM se control kar sakein
active_animations: dict[str, dict] = {}

SPACE_EMOJIS = ["🚀", "🛸", "☄️", "🌌", "🌟", "🛰️", "👨‍🚀", "✨", "🌍", "🪐"]

def generate_space_frame():
    # 6 rows aur 8 columns ka ek blank space grid banayenge
    # Yahan '　' (Ideographic Space) use kiya hai taaki Telegram blank spaces ko delete na kare
    grid = [["　" for _ in range(8)] for _ in range(6)]
    
    # Har frame me 5 se 8 random emojis grid me place karenge
    num_emojis = random.randint(5, 8)
    for _ in range(num_emojis):
        r = random.randint(0, 5) # Row
        c = random.randint(0, 7) # Column
        grid[r][c] = random.choice(SPACE_EMOJIS)
        
    return "\n".join(["".join(row) for row in grid])

async def run_space_loop(msg: Message):
    try:
        while True:
            # Naya random frame generate karo
            frame = generate_space_frame()
            # Telegram ki edit limits cross na ho isliye 1.5 sec delay
            await asyncio.sleep(1.5)
            try:
                # Bina kisi inline button ke pure text edit hoga
                await msg.edit_text(frame)
            except Exception as e:
                logging.error(f"Frame edit error: {e}")
    except asyncio.CancelledError:
        pass


# ==========================================
# 4. BOT HANDLERS (Channel + DM Control)
# ==========================================
@dp.channel_post(Command("start"))
@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    await message.answer(
        "Hello! 👋 Main Space Animation Bot hoon.\n\n"
        "🌌 Animation start karne ke liye (Channel ya DM me): /rocket\n"
        "🔗 Bot ke DM me aakar link reveal karne ke liye: `/addlink [aapka_link]`\n"
        "🛑 Bot ke DM se animation rokne ke liye: `/stop`"
    )

# Rocket start karna (Channel ya Group me)
@dp.channel_post(Command("rocket"))
@dp.message(Command("rocket"))
async def start_rocket(message: types.Message):
    if "current" in active_animations:
        # Agar pehle se chal raha hai to naya start nahi karenge
        await message.answer("⚠️ Ek animation pehle se live hai!")
        return

    # Pehla frame generate karke bina button ke bhejenge
    first_frame = generate_space_frame()
    msg = await message.answer(first_frame)
    
    task = asyncio.create_task(run_space_loop(msg))
    
    # Task ko global variable me save kar lenge taaki DM se access kar sakein
    active_animations["current"] = {"task": task, "message": msg}
    
    # Optional: Command wale message ko delete kar do taaki chat clean rahe
    try:
        await message.delete()
    except Exception:
        pass


# Bot DM se animation rok kar Link lagana
@dp.message(Command("addlink"))
async def add_link(message: types.Message):
    args = message.text.split(maxsplit=1)
    link = args[1] if len(args) > 1 else None
    
    if "current" in active_animations:
        active_animations["current"]["task"].cancel()
        target_msg = active_animations["current"]["message"]
        
        if link:
            # Channel wale message me link update hoga
            await target_msg.edit_text(f"🚀 **Target Reached!**\n\n🔗 Here is your link:\n{link}", parse_mode="Markdown")
            await message.answer("✅ Channel ka animation stop ho gaya aur link add kar diya gaya!")
        else:
            await target_msg.edit_text("🛑 Animation Stopped.", parse_mode="Markdown")
            await message.answer("⚠️ Aapne koi link nahi diya, par channel ka animation rok diya gaya hai.")
            
        del active_animations["current"]
    else:
        await message.answer("⚠️ Abhi kisi bhi channel me koi animation nahi chal raha hai.")


# Sirf animation rokna (Bina link ke)
@dp.message(Command("stop"))
async def stop_animation(message: types.Message):
    if "current" in active_animations:
        active_animations["current"]["task"].cancel()
        target_msg = active_animations["current"]["message"]
        await target_msg.edit_text("🌌 Space journey paused.")
        del active_animations["current"]
        await message.answer("✅ Animation successfully rok diya gaya hai.")
    else:
        await message.answer("⚠️ Koi active animation nahi hai.")


# ==========================================
# 5. MAIN EXECUTION
# ==========================================
async def main():
    print("🚀 Space Bot is starting...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(
        bot,
        allowed_updates=["message", "channel_post", "callback_query"]
    )

if __name__ == "__main__":
    keep_alive()
    asyncio.run(main())
    
