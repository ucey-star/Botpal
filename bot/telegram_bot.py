import os
import json
import random
import datetime
import threading
import time
import requests
from flask import Flask
from pytz import timezone
from dotenv import load_dotenv

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)

################################################################################
# 1. Flask "dummy server" (health check endpoint)
################################################################################
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running!"

def run_flask_app():
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

################################################################################
# 2. Self-ping function (to keep the Render free tier alive, if possible)
################################################################################
def self_ping():
    while True:
        try:
            # Replace with your actual Render URL:
            requests.get("https://botpal.onrender.com")
            print("Pinged successfully!")
        except Exception as e:
            print("Failed to ping:", e)
        time.sleep(900)  # Ping every 15 minutes

################################################################################
# 3. Utility functions for chat IDs
################################################################################
CHAT_IDS_FILE = "chat_ids.json"

def load_chat_ids():
    if os.path.exists(CHAT_IDS_FILE):
        with open(CHAT_IDS_FILE, "r") as file:
            return json.load(file)
    return []

def save_chat_ids(chat_ids):
    with open(CHAT_IDS_FILE, "w") as file:
        json.dump(chat_ids, file)

################################################################################
# 4. Load messages from JSON
################################################################################
def load_messages():
    messages_path = os.path.join(os.path.dirname(__file__), 'messages.json')
    with open(messages_path, 'r') as file:
        return json.load(file)

################################################################################
# 5. /start command handler
################################################################################
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    chat_ids = load_chat_ids()

    if chat_id not in chat_ids:
        chat_ids.append(chat_id)
        save_chat_ids(chat_ids)
        await update.message.reply_text(
            "🎉 Happy Birthday! 🎂 I was engineered by Uche as a special birthday gift..."
        )
    else:
        await update.message.reply_text("Stay tuned for more messages. 😊")

################################################################################
# 6. Daily message-sending task (runs at 9:00 AM PST)
################################################################################
async def send_daily_message(context: ContextTypes.DEFAULT_TYPE):
    chat_ids = load_chat_ids()
    messages = load_messages()
    message = random.choice(messages)['message']
    full_message = f"🌟 Message for the Day: 🌟\n\n{message}"

    for chat_id in chat_ids:
        try:
            await context.bot.send_message(chat_id=chat_id, text=full_message)
        except Exception as e:
            print(f"Failed to send message to {chat_id}: {e}")

################################################################################
# 7. Main: Build the application, schedule the daily job, start threads, etc.
################################################################################
if __name__ == "__main__":
    load_dotenv()
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

    # Build the telegram bot application
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # Register /start
    application.add_handler(CommandHandler("start", start_command))

    # Schedule the job to run daily at 9:00 AM Pacific Time
    pacific_tz = timezone("US/Pacific")
    target_time = datetime.time(hour=9, minute=0, tzinfo=pacific_tz)
    application.job_queue.run_daily(send_daily_message, time=target_time)

    # Start the Flask app in one thread
    threading.Thread(target=run_flask_app, daemon=True).start()

    # Start the self-ping function in another thread
    threading.Thread(target=self_ping, daemon=True).start()

    print("Bot is running... Press Ctrl+C to stop.")
    application.run_polling()
