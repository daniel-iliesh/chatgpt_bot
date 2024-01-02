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
    response = requests.get(
        f"https://api.telegram.org/bot{os.environ['BOTFATHER_API_KEY']}/getWebhookInfo"
    )
    data = response.json()
    if "last_error_message" in data["result"]:
        app.logger.debug(f"Webhook Error: {data['result']['last_error_message']}")
        return False
    return True


@app.route(f"/{os.environ['BOTFATHER_API_KEY']}", methods=["POST"])
@app.route(f"/", methods=["POST"])
def webhook_handler():
    try:
        payload = request.get_json()
        message = payload.get("message")
        if message:
            chat_type = message["chat"]["type"]
            if "@" + bot.get_me().username in message["text"] and chat_type in [
                "group",
                "supergroup",
                "private",
            ]:
                bot.sender(message)
            elif chat_type == "private":
                bot.private_sender(message)
            bot.listen_chat(message)
    except Exception as e:
        app.logger.error(f"Exception on / [POST]: {e}", exc_info=True)

    return "", 200


if __name__ == "__main__":
    if check_webhook():
        bot.start()
