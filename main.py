from flask import Flask, request
import logging
from bot import Bot

app = Flask(__name__)  # Create your Flask app instance
bot = Bot()  # Pass the Flask app instance to your Bot class

# Configure logging
logging.basicConfig(level=logging.DEBUG)

@app.route('/', methods=['POST'])
def webhook_handler():
    if request.method == 'POST':
        update = request.get_json()

        # Log the received update for debugging
        logging.debug(f"Received update: {update}")

        if 'message' in update:
            message = update['message']

            # Log the received message for debugging
            logging.debug(f"Received message: {message}")

            bot.handle_message(message)
    
    return 'OK'

if __name__ == "__main__":
    bot.start()
