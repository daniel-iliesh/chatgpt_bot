from telebot import TeleBot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telebot import types
import os
import traceback
import dotenv
from chat import ChatBot
import datetime

dotenv.load_dotenv(dotenv.find_dotenv())
chatBot = ChatBot(teleBot.get_me())

class Bot:
    def __init__(self, teleBot):
        self.teleBot = teleBot
        self.me = teleBot.get_me()

    def create_chat_mode_menu(self):
        chatBot.set_prompts_options()
        buttons = [KeyboardButton(option) for option in chatBot.prompts_options.keys()]
        menu = ReplyKeyboardMarkup(row_width=2)
        menu.add(*buttons)
        return menu

    def handle_message(self, message):
        # Now you can use the Message object with teleBot
        chat_id = message.chat.id
        self.teleBot.send_chat_action(chat_id, "typing")
        response = chatBot.request(message)

        self.teleBot.reply_to(message, response, parse_mode="Markdown")

    def handle_callback_query(self, callback_query):
        # Extract the necessary information from the callback_query
        chat_id = callback_query["message"]["chat"]["id"]
        data = callback_query["data"]

        # Handle the callback query here
        # For example, you might want to send a message to the chat
        self.teleBot.send_message(chat_id, f"You clicked a button! The data was: {data}")
        self.teleBot.send_chat_action(chat_id, "typing")
        response = chatBot.request(callback_query["message"])
        self.teleBot.reply_to(callback_query["message"], response, parse_mode="Markdown")

    def start(self):
        print("Bot Started!")

        # Handle commands
        @self.teleBot.message_handler(commands=["start"])
        def start_message(message):
            self.teleBot.reply_to(message, "Здравствуйте братья!")

        @self.teleBot.message_handler(commands=["bot_mode"])
        def choosemode(message):
            self.teleBot.reply_to(
                message,
                "Выберите режим бота: ",
                reply_markup=self.create_chat_mode_menu(),
            )

        @self.teleBot.message_handler(commands=["clear_chat"])
        def clear_chat(message):
            chatBot.clear_chat(message.chat.id)
            self.teleBot.reply_to(
                message,
                f"Я забыл все о чем мы до этого говорили. Начнем с чистого листа.",
            )

        @self.teleBot.message_handler(commands=["reset"])
        def reset(message):
            chatBot.init_chat(message.chat.id, reset=True)
            self.teleBot.reply_to(message, f"Режим бота сброшен!")
        
        @self.teleBot.message_handler(commands=["active_mode"])
        def active_mode(message):
            if (self.active_mode == False):
                self.active_mode = True
                self.teleBot.reply_to(message, "Активный режим включен. Теперь буду отвечать на все сообщения.")
            else:
                self.active_mode = False
                self.teleBot.reply_to(message, "Активный режим выключен. Теперь буду отвечать только когда отмечают.")

        # Handle the 'mode selection' action
        @self.teleBot.message_handler(
            func=lambda message: message.text in chatBot.prompts_options.keys()
        )
        def handle_option_selected(message):
            selected_option = message.text
            chatBot.set_bot_mode(selected_option, message.chat.id)
            reply_markup = ReplyKeyboardRemove()
            self.teleBot.reply_to(
                message,
                text=f"Все, я теперь {selected_option}.",
                reply_markup=reply_markup,
            )

        def sender(self, message):
                self.handle_message(message)

        def private_sender(self, message):
            self.handle_message(message)

        def listen_chat(self, message):
            chatBot.update_context(message)