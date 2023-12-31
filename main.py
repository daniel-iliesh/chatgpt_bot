from flask import Flask, request
from bot import Bot

app = Flask(__name__)  # Create your Flask app instance
bot = Bot(app)  # Pass the Flask app instance to your Bot class

@app.route('/', methods=['POST'])
def webhook_handler():
    if request.method == 'POST':
        update = request.get_json()
        message = update['message']
        bot.handle_message(message)
    return 'OK'

if __name__ == "__main__":
    bot.start()
