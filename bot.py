from telebot import TeleBot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
import os
import traceback
import dotenv
from chat import ChatBot

dotenv.load_dotenv(dotenv.find_dotenv())
teleBot = TeleBot(os.getenv("BOTFATHER_API_KEY"))
chatBot = ChatBot(teleBot.get_me())

class Bot: 

    def __init__(self) -> None:
        pass

    def create_chat_mode_menu(self):
        chatBot.set_prompts_options()
        buttons = [KeyboardButton(option) for option in chatBot.prompts_options.keys()]
        menu = ReplyKeyboardMarkup(row_width=2)
        menu.add(*buttons)
        return menu
    
    def handle_message(self, message):
        teleBot.send_chat_action(message.chat.id, 'typing')
        teleBot.reply_to(message, chatBot.request(message))
    
    def start(self):

        while True:
            try:
                print("Bot Started!")
                # Handle commands
                @teleBot.message_handler(commands=['start'])
                def start_message(message):
                    teleBot.reply_to(message, "Здравствуйте букашки!")

                @teleBot.message_handler(commands=['bot_mode'])
                def choosemode(message):
                    teleBot.reply_to(message, 'Выберите режим бота: ', reply_markup=self.create_chat_mode_menu())

                @teleBot.message_handler(commands=['clear_chat'])
                def clear_chat(message):
                    chatBot.clear_chat(message.chat.id)
                    teleBot.reply_to(message, f'Чат отчищен!')

                @teleBot.message_handler(commands=['reset'])
                def reset(message):

                    teleBot.reply_to(message, f'Чат отчищен!')

                # Handle messages
                # Handle reffering to the bot by tagging him in groups and in private

                 # Handle the 'mode selection' action
                @teleBot.message_handler(func=lambda message: message.text in chatBot.prompts_options.keys())
                def handle_option_selected(message):
                    selected_option = message.text
                    chatBot.set_bot_mode(selected_option, message.chat.id)
                    reply_markup = ReplyKeyboardRemove()
                    teleBot.reply_to(message, text=f'Все, я теперь {selected_option}.', reply_markup=reply_markup)
                    
                @teleBot.message_handler(func=lambda message: '@' + teleBot.get_me().username in message.text, chat_types=['group', 'supergroup', 'private'])
                def sender(message):
                    # print("Handle tagged bot\n")
                    self.handle_message(message)

                # Handle all messages in private chats
                @teleBot.message_handler(func=lambda message: True, chat_types=['private'])
                def private_sender(message):
                    self.handle_message(message)

                # Listen all messages to add them in the chat memory for context
                @teleBot.message_handler(func=lambda message: True)
                def listen_chat(message):
                    chatBot.update_context(message)

                teleBot.polling()

            except Exception as e:
                teleBot.stop_polling()
                traceback.print_exc()

bot = Bot()
bot.start()