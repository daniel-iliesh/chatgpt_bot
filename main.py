import logging
from bot import Bot

# Configure logging
logging.basicConfig(level=logging.DEBUG)

if __name__ == "__main__":
    bot = Bot() 
    bot.start() 
    bot.start_polling() 