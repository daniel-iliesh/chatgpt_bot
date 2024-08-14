import re
from telegram import Update
from telegram.ext import CallbackContext
import telegramify_markdown


def bot_mentioned(update: Update, context: CallbackContext) -> bool:
    bot_username = context.bot.username
    return f"@{bot_username}" in update.message.text


def escape_markdown_v2(text: str) -> str:
    return telegramify_markdown.markdownify(text)