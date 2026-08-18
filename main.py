import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.enums import ButtonStyle

# Active animations ko track karne ke liye (Task aur Message dono store karenge)
active_animations: dict[int, dict] = {}

ROCKET_FRAMES = ["🚀 . . .", ". 🚀 . .", ". . 🚀 .", ". . . 🚀", ". . 🚀 .", ". 🚀 . ."]

stop_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="🛑 Stop Animation", callback_data="stop_rocket", style=ButtonStyle.DANGER)
        ]
    ]
)

# Background Loop
async def run_rocket_loop(msg: types.Message):
    try:
        while True:
            for frame in ROCKET_FRAMES:
                await asyncio.sleep(1.3)
                await msg.edit_text(frame, reply_markup=stop_keyboard)
    except asyncio.CancelledError:
        # Loop cancel hote hi yahan aa jayega
        pass

@dp.message(Command("rocket"))
async def start_rocket(message: types.Message):
    chat_id = message.chat.id
    if chat_id in active_animations:
        await message.answer("⚠️ Animation pehle se chal raha hai!")
        return

    msg = await message.answer(ROCKET_FRAMES[0], reply_markup=stop_keyboard)
    task = asyncio.create_task(run_rocket_loop(msg))
    
    # Task aur Message object dono save kar rahe hain
    active_animations[chat_id] = {"task": task, "message": msg}

@dp.message(Command("addlink"))
async def add_link(message: types.Message):
    chat_id = message.chat.id
    
    # Link nikalna (command ke baad ka text)
    args = message.text.split(maxsplit=1)
    link = args[1] if len(args) > 1 else None
    
    if chat_id in active_animations:
        # 1. Animation Task Cancel karo
        active_animations[chat_id]["task"].cancel()
        
        # 2. Wahi animated message edit karke link dikhao
        msg = active_animations[chat_id]["message"]
        if link:
            await msg.edit_text(f"✅ Success! Link added: {link}", reply_markup=None)
        else:
            await msg.edit_text("🛑 Animation stopped (No link added).", reply_markup=None)
            
        del active_animations[chat_id]
        await message.delete() # Command message delete kar do taaki chat saaf rahe
    else:
        await message.answer("⚠️ Koi active animation nahi mil raha hai.")

@dp.callback_query(F.data == "stop_rocket")
async def stop_rocket_callback(callback: types.CallbackQuery):
    chat_id = callback.message.chat.id
    if chat_id in active_animations:
        active_animations[chat_id]["task"].cancel()
        await callback.message.edit_text("🛑 Animation stopped.", reply_markup=None)
        del active_animations[chat_id]
        await callback.answer("Stopped!")
      
