from email.mime import message
import os
from agents import function_tool
import requests
from telegram import Bot


TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

@function_tool
async def send_notification(notification: str):
    """Sends a notification to the user.

    Args:
        notification (str): The notification message to send.
    """
    print("Creating Telegram Bot client...")
    print("TELEGRAM_TOKEN: ", TELEGRAM_TOKEN)
    print("TELEGRAM_CHAT_ID: ", TELEGRAM_CHAT_ID)
    # Initialize Telegram Bot
    tg_bot = Bot(token=TELEGRAM_TOKEN)
    print("Sending notification to user:")
    print(notification)
    await tg_bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=f"🤖 Agent Alert: {notification}")
    print("Notification sent!")

# @function_tool
# def send_notification(notification: str):
#     """Sends a notification to the user.

#     Args:
#         notification (str): The notification message to send.
#     """
#     print("Creating Telegram Bot client...")
#     # Initialize Telegram Bot
#     tg_bot = Bot(token=TELEGRAM_TOKEN)
#     print("Sending notification to user:")
#     print(notification)
#     # await tg_bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=f"🤖 Agent Alert: {notification}")
#     print("Notification sent!")