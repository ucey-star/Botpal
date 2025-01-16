import os
import json
import random
from dotenv import load_dotenv
from twilio.rest import Client

# Load environment variables
load_dotenv()
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_WHATSAPP_NUMBER = os.getenv('TWILIO_WHATSAPP_NUMBER')

# Initialize Twilio client
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Predefined recipients
RECIPIENTS = [
    "whatsapp:+14156453460",  # Replace with your girlfriend's WhatsApp number
]

# Load messages from a JSON file
def load_messages():
    with open('messages.json', 'r') as file:
        return json.load(file)

# Send a random message
def send_whatsapp_message():
    messages = load_messages()
    message_text = random.choice(messages)['message']  # Randomly select a message
    full_message = f"🌟 Message for the Day: 🌟\n\n{message_text}"

    for recipient in RECIPIENTS:
        try:
            message = client.messages.create(
                from_=TWILIO_WHATSAPP_NUMBER,
                body=full_message,
                to=recipient
            )
            print(f"Message sent to {recipient}: {message.sid}")
        except Exception as e:
            print(f"Failed to send message to {recipient}: {e}")

if __name__ == "__main__":
    send_whatsapp_message()
