import os
from agents import function_tool
import requests


@function_tool
def send_notification(notification: str):
    """Sends a notification to the user.

    Args:
        notification (str): The notification message to send.
    """
    print("Sending notification to user:")
    pushover_user = os.getenv("PUSHOVER_USER")
    pushover_token = os.getenv("PUSHOVER_TOKEN")
    pushover_url = "https://api.pushover.net/1/messages.json"

    message = notification

    print(f"Push: {message}")
    payload = {"user": pushover_user, "token": pushover_token, "message": message}
    requests.post(pushover_url, data=payload)