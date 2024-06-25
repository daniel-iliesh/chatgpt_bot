from telebot import TeleBot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telebot import types
import os
import dotenv
import logging
from chat import ChatBot

dotenv.load_dotenv(dotenv.find_dotenv())
teleBot = TeleBot(os.environ["BOTFATHER_API_KEY"])
chatBot = ChatBot(teleBot.get_me())

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Bot:
    def __init__(self):
        pass

    def create_chat_mode_menu(self):
        chatBot.set_prompts_options()
        buttons = [KeyboardButton(option) for option in chatBot.prompts_options.keys()]
        menu = ReplyKeyboardMarkup(row_width=2)
        menu.add(*buttons)
        return menu

    def handle_message(self, message):
        chat_id = message.chat.id
        teleBot.send_chat_action(chat_id, "typing")
        response = chatBot.request(message)
        teleBot.reply_to(message, response, parse_mode="Markdown")

    def handle_callback_query(self, callback_query):
        # Extract the necessary information from the callback_query
        chat_id = callback_query["message"]["chat"]["id"]
        data = callback_query["data"]

        # Handle the callback query here
        # For example, you might want to send a message to the chat
        teleBot.send_message(chat_id, f"You clicked a button! The data was: {data}")
        chat_id = self.message.chat.id
        teleBot.send_chat_action(chat_id, "typing")
        response = chatBot.request(self.message)
        teleBot.reply_to(self.message, response, parse_mode="Markdown")

    def start(self):
        logging.debug("Bot Started!")

        # Handle commands
        @teleBot.message_handler(commands=["start"])
        def start_message(message):
            teleBot.reply_to(message, "Здравствуйте букашки!")

        @teleBot.message_handler(commands=["bot_mode"])
        def choosemode(message):
            teleBot.reply_to(
                message,
                "Выберите режим бота: ",
                reply_markup=self.create_chat_mode_menu(),
            )

        @teleBot.message_handler(commands=["clear_chat"])
        def clear_chat(message):
            chatBot.clear_chat(message.chat.id)
            teleBot.reply_to(
                message,
                f"Я забыл все о чем мы до этого говорили. Начнем с чистого листа.",
            )

        @teleBot.message_handler(commands=["reset"])
        def reset(message):
            chatBot.init_chat(message.chat.id, reset=True)
            teleBot.reply_to(message, f"Режим бота сброшен!")

        # Handle the 'mode selection' action
        @teleBot.message_handler(
            func=lambda message: message.text in chatBot.prompts_options.keys()
        )
        def handle_option_selected(message):
            selected_option = message.text
            chatBot.set_bot_mode(selected_option, message.chat.id)
            reply_markup = ReplyKeyboardRemove()
            teleBot.reply_to(
                message,
                text=f"Все, я теперь {selected_option}.",
                reply_markup=reply_markup,
            )

        @teleBot.message_handler(
            func=lambda message: "@" + teleBot.get_me().username in message.text,
            chat_types=["group", "supergroup", "private"],
        )
        def sender(message):
            self.handle_message(message)

        # Handle all messages in private chats
        @teleBot.message_handler(func=lambda message: True, chat_types=["private"])
        def private_sender(message):
            self.handle_message(message)

        # Listen all messages to add them in the chat memory for context
        @teleBot.message_handler(func=lambda message: True)
        def listen_chat(message):
            chatBot.update_context(message)

    def start_polling(self):
        logging.debug("Removing webhook and starting polling...")
        teleBot.remove_webhook()  # Ensure the webhook is removed
        teleBot.polling(none_stop=True)  # Start polling
