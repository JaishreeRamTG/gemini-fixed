import os
import requests
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
API_URL = "https://gemini-fixed.vercel.app/pythonbotz?msg={}"

app = Flask(__name__)

# Telegram Bot Setup
bot_app = Application.builder().token(TOKEN).build()

async def start(update: Update, context):
    await update.message.reply_text("Hey there! I'm your chatbot. Send me a message and I'll reply!")

async def handle_message(update: Update, context):
    user_message = update.message.text
    response = requests.get(API_URL.format(user_message)).json()
    reply_text = response.get("reply", "Sorry, I couldn't fetch a response.")
    
    await update.message.reply_text(reply_text)

# Register Handlers
bot_app.add_handler(CommandHandler("start", start))
bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# Flask Route for Webhook
@app.route("/webhook", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(), bot_app.bot)
    bot_app.update_queue.put(update)
    return "OK", 200

if __name__ == "__main__":
    bot_app.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        webhook_url=os.getenv("WEBHOOK_URL")  # Set this in Vercel env variables
    )