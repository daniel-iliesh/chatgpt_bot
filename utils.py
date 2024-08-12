import re
from telegram import Update
from telegram.ext import CallbackContext


def bot_mentioned(update: Update, context: CallbackContext) -> bool:
    bot_username = context.bot.username
    return f"@{bot_username}" in update.message.text


def escape_markdown_v2(text: str) -> str:
    """
    Escapes the characters in a string for safe use with MarkdownV2 parse mode in Telegram.
    """
    escape_chars = r"_*[]()~`>#+-=|{}.!\\"
    return re.sub(f"([{re.escape(escape_chars)}])", r"\\\1", text)
