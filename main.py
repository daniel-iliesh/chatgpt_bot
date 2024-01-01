import os
import requests
from flask import Flask, request
import logging
from bot import Bot

app = Flask(__name__)  # Create your Flask app instance
bot = Bot()  # Pass the Flask app instance to your Bot class
# Configure logging
logging.basicConfig(level=logging.DEBUG)

def check_webhook():
    response = requests.get(f"https://api.telegram.org/bot{os.environ['BOTFATHER_API_KEY']}/getWebhookInfo")
    data = response.json()
    if 'last_error_message' in data['result']:
        app.logger.debug(f"Webhook Error: {data['result']['last_error_message']}")
        return False
    return True

@app.route(f"/{os.environ['BOTFATHER_API_KEY']}", methods=['POST'])
def webhook_handler():
    try:
        payload = request.get_json()
        app.logger.debug(f"Received update: {payload}")
        
        if 'message' in payload:
            # This is a message update
            message = payload['message']
            app.logger.debug(f"Received message: {message}")
            bot.handle_message(message)
        elif 'callback_query' in payload:
            # This is a callback query update
            callback_query = payload['callback_query']
            bot.handle_callback_query(callback_query)
        # Add more elif clauses here for other update types
        else:
            app.logger.error(f"Unknown update: {payload}")

    except Exception as e:
        app.logger.error(f"Exception on / [POST]: {e}", exc_info=True)

    return '', 200


if __name__ == "__main__":
    if (check_webhook()):
        bot.start()
