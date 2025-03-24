import os

import requests
from dotenv import load_dotenv

from .base import Notifier


class TelegramNotifier(Notifier):
    def __init__(self, token: str, chat_id: str):
        self.token = token
        self.chat_id = chat_id

    def send_message(self, msg: str):
        """
        Send a message to the Telegram chat bot
        param msg: message to send
        """
        url = f'https://api.telegram.org/bot{self.token}/sendMessage?chat_id={self.chat_id}&text={msg}'
        try:
            response = requests.get(url)
            response.raise_for_status()
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Telegram Error: {e}")
            
def test_send_message():
    load_dotenv()
    chat_token = os.getenv("CHAT_TOKEN")
    chat_id = os.getenv("CHAT_ID")    
    notifier = TelegramNotifier(chat_token, chat_id)
    notifier.send_message("Hello, World!")
    
if __name__ == "__main__":
    test_send_message()
    
    # Initialize the TelegramNotifier    
    load_dotenv()
    chat_token = os.getenv("CHAT_TOKEN")
    chat_id = os.getenv("CHAT_ID")
    notier = TelegramNotifier(chat_token, chat_id)
    
    # Send a message to the Telegram chat bot
    msg = "Hello, World!"
    notier.send_message(msg)