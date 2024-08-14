from ast import parse
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters
from utils import bot_mentioned, escape_markdown_v2
from chat import ChatBot

chat_bot = ChatBot()

async def on_greeting(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'Hello {update.effective_user.first_name}')

async def on_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if bot_mentioned(update, context):
        await context.bot.send_chat_action(chat_id=update.message.chat_id, action="typing")
        response = chat_bot.request(update.message, context.bot)
        escaped_response = escape_markdown_v2(response)
        print("Escaped response", escaped_response)
        await update.message.reply_markdown_v2(escaped_response)
    else:
        chat_bot.update_context(update.message, context.bot)

# Commands handlers
greeting_handler = CommandHandler("hello", on_greeting)

# Message handlers
any_message_handler = MessageHandler(filters.ALL, on_message)