import asyncio
import logging
from telegram import Update
from telegram.ext import ContextTypes
import sqlite3
import os

DB_PATH = os.getenv("DATABASE_URL", "bot_database.db")

async def broadcast_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("الرجاء كتابة الرسالة بعد الأمر. مثال: /broadcast أهلاً بكم")
        return

    message_text = " ".join(context.args)
    conn = sqlite3.connect(DB_PATH)
    users = conn.execute('SELECT user_id FROM users').fetchall()
    conn.close()

    success = 0
    failed = 0

    for user in users:
        try:
            await context.bot.send_message(chat_id=user[0], text=message_text)
            success += 1
            await asyncio.sleep(0.05) # تجنب الحظر من تلجرام
        except Exception as e:
            failed += 1
            logging.error(f"Failed to send to {user[0]}: {e}")

    await update.message.reply_text(f"✅ تم الانتهاء من الإذاعة:\n- نجاح: {success}\n- فشل: {failed}")
