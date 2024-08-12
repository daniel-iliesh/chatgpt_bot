import os
from telegram.ext import ApplicationBuilder
from dotenv import load_dotenv

from handlers import greeting_handler, any_message_handler

load_dotenv()

app = ApplicationBuilder().token(os.getenv("BOTFATHER_API_KEY")).build()

# Commands handlers 
app.add_handler(greeting_handler)

# Message handlers
app.add_handler(any_message_handler)

app.run_polling()
