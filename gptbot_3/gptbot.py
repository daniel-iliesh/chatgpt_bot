from telebot import TeleBot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
import os, openai
import traceback
import dotenv
import csv

dotenv.load_dotenv(dotenv.find_dotenv())
openai.api_key = os.getenv("OPENAI_API_KEY")
botFatherKey = os.getenv("BOTFATHER_API_KEY")
teleBot = TeleBot(botFatherKey)
options = []

with open('prompts_ru.csv', 'r') as file:
    csv_reader = csv.reader(file)

with open('prompts_ru.csv', 'r') as file:
    csv_reader = csv.reader(file)
    for row in csv_reader:
        # print(f"Row: {row[0]}\nColumn: {row[1]}\n")    
        options.append(row[0])
    
    buttons = [KeyboardButton(option) for option in options]
    menu = ReplyKeyboardMarkup(row_width=2)
    menu.add(*buttons)

class ChatBot:
    chat_mode = ""
    dialogues = {}
    
    def __init__(self) -> None:
        pass

    def generate_prompt(self, current_message):
        prompt = self.chat_mode
        prompt += "\n"
        
        for chat_id, messages in self.dialogues.items():
            for user, message in messages:
                prompt += f"{user}: {message}\n"

        prompt += f"{current_message.from_user.username}: {current_message.text}\n"
        self.update_dialogue(current_message)

        return prompt
    
    def _postprocess_answer(self, answer):
        answer = answer.strip()
        answer = answer.split(": ")
        if len(answer) > 1: 
            return answer[1]
        else:
            return answer[0]
    
    def update_dialogue(self, message, chatId=0, gpt_answer=False):
        if gpt_answer == False : 
            chat_id = message.chat.id
            user = f"{message.from_user.first_name}({message.from_user.username})"
            text = message.text
        
            if chat_id in self.dialogues:
                # Append new message to existing chat
                self.dialogues[chat_id].append((user, text))
            else:
                # Create new chat with first text
                self.dialogues[chat_id] = [(user, text)]
        else: 
            self.dialogues[chatId].append(("BadBot", message))

    def request(self, message):
        prompt = self.generate_prompt(message)
        response = openai.Completion.create(
            model="gpt-3.5-turbo",
            prompt=self.chat_mode + prompt,
            temperature=0.7, # controls the level of randomness in the generated text. A higher temperature value will produce more diverse and creative responses, while a lower value will produce more predictable responses.
            max_tokens=256,
            top_p=1.0,
            stop=None,
            frequency_penalty=0.6, # encourages the model to avoid using the same words or phrases too often in the generated text. This can help make the conversation feel more varied and interesting.
            best_of=1,
            presence_penalty=0.6 # encourages the model to avoid repeating phrases or concepts that have already been mentioned in the conversation.This can help make the conversation feel more natural and less repetitive.
        )
        result = self._postprocess_answer(response["choices"][0]["text"])
        self.update_dialogue(result, message.chat.id, gpt_answer=True)
        return result
    
    def choose_mode(self, new_mode):
        with open('prompts_ru.csv', 'r') as file:
            csv_reader = csv.reader(file)
            for row in csv_reader:
                if row[0] == new_mode: 
                    self.chat_mode = row[1]
                    print(f"Now the chat mode is: {row[0]}")
        print(self.chat_mode)

    def log_dialog(self):
        for chat_id, messages in self.dialogues.items():
            for user, message in messages:
                print(f"{user}: {message}\n")

chatBot = ChatBot()

def handle_message(message):
    teleBot.reply_to(message, chatBot.request(message))
    chatBot.log_dialog()

while True:
    try:
        print("Bot Started!")

        @teleBot.message_handler(commands=['start'])
        def start_message(prompt):
            teleBot.reply_to(prompt, "Здравствуйте букашки!")

        @teleBot.message_handler(func=lambda prompt: '@' + teleBot.get_me().username in prompt.text, chat_types=['group', 'supergroup', 'private'])
        def sender(prompt):
            handle_message(prompt)
        # @teleBot.message_handler(content_types='text', chat_types=['group', 'supergroup', 'private'])
        # def active_sender(prompt):
        #     chatBot.update_dialogue(prompt)

        @teleBot.message_handler(content_types='text', chat_types=['private'])
        def private_sender(prompt):
            handle_message(prompt)

        @teleBot.message_handler(commands=['stop'])
        def stop_bot(prompt):
            teleBot.reply_to(prompt, "Я уйду, но вы об этом скоро пожелеете!")
            teleBot.stop_bot()

        @teleBot.message_handler(commands=['choosemode'])
        def choosemode(prompt): 
            teleBot.reply_to(prompt, 'Выберите режим бота: ', reply_markup=menu)

        @teleBot.message_handler(func=lambda prompt: prompt.text in options)
        def handle_option_selected(prompt):
            selected_option = prompt.text
            chatBot.choose_mode(selected_option)
            chatBot.dialogues = {}
            teleBot.reply_to(prompt, text=f'Все, я теперь {selected_option}.')  

        teleBot.polling()

    except Exception as e:
        teleBot.stop_polling()
        traceback.print_exc()




