from telebot import TeleBot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
import os
import traceback
import dotenv
from chat import ChatBot
import datetime

dotenv.load_dotenv(dotenv.find_dotenv())
teleBot = TeleBot(os.environ["BOTFATHER_API_KEY"])
chatBot = ChatBot(teleBot.get_me())

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
        teleBot.send_chat_action(message.chat.id, "typing")
        teleBot.reply_to(message, chatBot.request(message))
        chatBot.log_dialog()

    def start(self):
        print("Bot Started!")

        # Handle commands
        @teleBot.message_handler(commands=["start"])
        def start_message(message):
            teleBot.reply_to(message, "Здравствуйте букашки!")

        @teleBot.message_handler(commands=["bot_mode"])
        def choosemode(message):
            teleBot.reply_to(
                message, "Выберите режим бота: ", reply_markup=self.create_chat_mode_menu()
            )

        @teleBot.message_handler(commands=["clear_chat"])
        def clear_chat(message):
            chatBot.clear_chat(message.chat.id)
            teleBot.reply_to(
                message, f"Я забыл все о чем мы до этого говорили. Начнем с чистого листа."
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
                message, text=f"Все, я теперь {selected_option}.", reply_markup=reply_markup
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

        # Start polling
        teleBot.polling(none_stop=True)