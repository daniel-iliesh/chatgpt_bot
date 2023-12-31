from flask import Flask
from bot import Bot

app = Flask(__name__)  # Create your Flask app instance

if __name__ == "__main__":
    bot = Bot(app)  # Pass the Flask app instance to your Bot class
    bot.start()