from flask import Flask, request
import logging
from bot import Bot

app = Flask(__name__)  # Create your Flask app instance
bot = Bot()  # Pass the Flask app instance to your Bot class

# Configure logging
logging.basicConfig(level=logging.DEBUG)

@app.route('/', methods=['POST'])
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
        app.logger.error(f"Exception on / [POST]: {e}")

    return '', 200


if __name__ == "__main__":
    bot.start()
