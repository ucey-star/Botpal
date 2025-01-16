import os
import json
import random
import asyncio
from flask import Flask
import threading
from dotenv import load_dotenv
from telegram import Bot, Update
from telegram.ext import ApplicationBuilder, CommandHandler
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running!"

def run_dummy_server():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))


# Load environment variables
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# Initialize the bot
bot = Bot(token=TELEGRAM_BOT_TOKEN)
CHAT_IDS_FILE = "chat_ids.json"  # File to store chat IDs

# Load or initialize chat IDs
def load_chat_ids():
    if os.path.exists(CHAT_IDS_FILE):
        with open(CHAT_IDS_FILE, "r") as file:
            return json.load(file)
    return []  # Return an empty list if the file doesn't exist

def save_chat_ids(chat_ids):
    with open(CHAT_IDS_FILE, "w") as file:
        json.dump(chat_ids, file)

# Handle /start command
async def start(update: Update, context):
    chat_id = update.message.chat.id
    chat_ids = load_chat_ids()

    if chat_id not in chat_ids:
        chat_ids.append(chat_id)
        save_chat_ids(chat_ids)
        await update.message.reply_text(
            "🎉 Happy Birthday! 🎂 I was created by Uche, especially for you, as a birthday gift. My purpose is to send you motivational messages that remind you of your incredible strength, inspire your journey, and help you face insecurities with courage and confidence. Together, we’ll embrace every challenge, celebrate every triumph, and make this year your best one yet. 🌟"
        )
    else:
        await update.message.reply_text("Stay tuned for more messages. 😊")


# Load messages from a JSON file
def load_messages():
    with open('messages.json', 'r') as file:
        return json.load(file)

# Send a random message to all saved chat IDs
async def send_message():
    chat_ids = load_chat_ids()
    messages = load_messages()
    message = random.choice(messages)['message']  # Extract the actual message text

    # Add the introduction to the message
    full_message = f"🌟 Message for the Day: 🌟\n\n{message}"

    for chat_id in chat_ids:
        try:
            await bot.send_message(chat_id=chat_id, text=full_message)
        except Exception as e:
            print(f"Failed to send message to {chat_id}: {e}")


if __name__ == "__main__":
    # Initialize the Telegram bot application
    bot.delete_webhook(drop_pending_updates=True)
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # Register the /start command
    application.add_handler(CommandHandler("start", start))

    # Initialize the scheduler
    scheduler = BackgroundScheduler()
    scheduler.add_job(lambda: asyncio.run(send_message()), 'cron', hour=9, minute=0)  # Sends a message daily at 9 AM
    scheduler.start()

    print("Bot is running...")
    application.run_polling()
    