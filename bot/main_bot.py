import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from utils.database import init_db, add_user, get_active_keys
from utils.ai_handler import GeminiHandler
from bot.admin_features import broadcast_message
from dotenv import load_dotenv

load_dotenv()

# إعدادات البوت
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
CHANNEL_ID = os.getenv("CHANNEL_ID") # الاشتراك الإجباري

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

ai_handler = None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await add_user(user.id, user.username, user.full_name)
    
    # تحقق من الاشتراك الإجباري
    if CHANNEL_ID:
        try:
            member = await context.bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user.id)
            if member.status in ['left', 'kicked']:
                keyboard = [[InlineKeyboardButton("اشترك في القناة 📢", url=f"https://t.me/{CHANNEL_ID.replace('@', '')}")]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await update.message.reply_text("عذراً، يجب عليك الاشتراك في القناة أولاً لاستخدام البوت!", reply_markup=reply_markup)
                return
        except Exception as e:
            logging.error(f"Error checking sub: {e}")

    await update.message.reply_text(f"أهلاً بك {user.first_name} في بوت الذكاء الاصطناعي المتقدم! 🚀\n\nأنا أعمل بمحرك Gemini المتطور. كيف يمكنني مساعدتك اليوم؟")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global ai_handler
    if not ai_handler:
        keys = await get_active_keys()
        ai_handler = GeminiHandler(keys)

    user_text = update.message.text
    # إظهار حالة "يكتب..." (التكلم في الخلفية)
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    response = await ai_handler.get_response(user_text)
    await update.message.reply_text(response)

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    
    keyboard = [
        [InlineKeyboardButton("الإذاعة 📢", callback_data='broadcast')],
        [InlineKeyboardButton("إدارة المفاتيح 🔑", callback_data='manage_keys')],
        [InlineKeyboardButton("الإحصائيات 📊", callback_data='stats')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("مرحباً بك في لوحة المطور! اختر أحد الخيارات:", reply_markup=reply_markup)

async def main():
    await init_db()
    
    # تهيئة مفاتيح Gemini الأولية من البيئة
    initial_keys = [os.getenv(f"GEMINI_KEY_{i}") for i in range(1, 4) if os.getenv(f"GEMINI_KEY_{i}")]
    for key in initial_keys:
        await add_api_key(key)

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin_panel))
    app.add_handler(CommandHandler("broadcast", broadcast_message))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

    print("البوت يعمل الآن...")
    await app.run_polling()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
