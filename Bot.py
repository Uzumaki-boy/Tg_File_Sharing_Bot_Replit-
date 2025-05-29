import os
from telegram import Update, ChatMember
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import threading
from flask import Flask
from waitress import serve

BOT_TOKEN = os.environ.get("7625056610:AAH8dEqIzAHvnQPsBFiE5zKcPYAUOjHueuw")
CHANNELS = os.environ.get("@TamilMovieClub73", "@AnimeBorns").split(",")

files_db = {}

async def is_user_subscribed(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    user_id = update.effective_user.id
    for channel in CHANNELS:
        try:
            member = await context.bot.get_chat_member(channel, user_id)
            if member.status not in [ChatMember.MEMBER, ChatMember.ADMINISTRATOR, ChatMember.OWNER]:
                return False
        except:
            return False
    return True

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_user_subscribed(update, context):
        channel_list = "\n".join(CHANNELS)
        await update.message.reply_text(
            f"❗️ You must join our channels to use this bot:\n{channel_list}\nThen send /start again."
        )
        return
    await update.message.reply_text("👋 Welcome! Send any file and I'll give you a File ID.\nUse /get <file_id> to download.")

async def save_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_user_subscribed(update, context):
        await update.message.reply_text("❗ Please join the required channels first.")
        return

    file = update.message.document or update.message.video or update.message.audio or update.message.photo[-1] if update.message.photo else None

    if not file:
        await update.message.reply_text("❗ Unsupported file type.")
        return

    file_id = file.file_id
    files_db[file_id] = file_id
    await update.message.reply_text(f"✅ File saved!\nFile ID: `{file_id}`", parse_mode='Markdown')

async def get_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_user_subscribed(update, context):
        await update.message.reply_text("❗ Please join the required channels first.")
        return

    args = context.args
    if not args:
        await update.message.reply_text("❗ Usage: /get <file_id>")
        return

    file_id = args[0]
    if file_id in files_db:
        await update.message.reply_document(file_id)
    else:
        await update.message.reply_text("❌ File not found.")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("get", get_file))
    app.add_handler(MessageHandler(filters.Document.ALL | filters.Video.ALL | filters.Audio.ALL | filters.PHOTO, save_file))

    app.run_polling()

# Keep alive Flask server
flask_app = Flask("")

@flask_app.route('/')
def home():
    return "Bot is running."

def run():
    serve(flask_app, host="0.0.0.0", port=8080)

threading.Thread(target=run).start()
main()
