import os
import json
import random
import asyncio
from flask import Flask
import threading
import requests
import time
from pytz import timezone
from dotenv import load_dotenv
from telegram import Bot, Update
from telegram.ext import ApplicationBuilder, CommandHandler
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.events import EVENT_JOB_ERROR

app = Flask(__name__)
pacific = timezone('US/Pacific')

@app.route("/")
def home():
    return "Bot is running!"

def run_dummy_server():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))


def self_ping():
    while True:
        try:
            requests.get("https://botpal.onrender.com")
            print("Pinged successfully!")
        except Exception as e:
            print(f"Failed to ping: {e}")
        time.sleep(900)  # Ping every 15 minutes

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
            "🎉 Happy Birthday! 🎂 I was engineered by Uche as a special birthday gift just for you. My mission is to send you uplifting messages that celebrate your strength, inspire your journey, and help you face insecurities with courage and grace. Together, we’ll tackle challenges, celebrate victories, and make this year truly unforgettable. 🌟 Remember, our bodies change with the seasons—embrace and love yourself through every phase of life. 💖"
        )
    else:
        await update.message.reply_text("Stay tuned for more messages. 😊")


# Load messages from a JSON file
def load_messages():
    # Get the absolute path of the current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Construct the full path to messages.json
    messages_path = os.path.join(current_dir, 'messages.json')

    with open(messages_path, 'r') as file:
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

# Function to schedule asynchronous jobs properly
def schedule_async(func):
    asyncio.run(func())

if __name__ == "__main__":
    # Initialize the Telegram bot application
    threading.Thread(target=run_dummy_server, daemon=True).start()
    threading.Thread(target=self_ping, daemon=True).start()
    bot.delete_webhook(drop_pending_updates=True)
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # Register the /start command
    application.add_handler(CommandHandler("start", start))

    # Initialize the scheduler
    scheduler = BackgroundScheduler(timezone=pacific)

    # Add a job to the scheduler for 9:50 AM Pacific Time
    scheduler.add_job(lambda: schedule_async(send_message), 'interval', minutes=5)

    # Listener for debugging scheduler errors
    def job_listener(event):
        if event.exception:
            print(f"Job failed: {event.job_id} - {event.exception}")
    scheduler.add_listener(job_listener, EVENT_JOB_ERROR)

    scheduler.start()

    print("Bot is running...")
    application.run_polling()
