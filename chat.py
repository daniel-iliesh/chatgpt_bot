# -*- coding: utf-8 -*-
import os
import openai
import csv
import dotenv
import json

dotenv.load_dotenv(dotenv.find_dotenv())
openai.api_base = os.environ["OPENAI_API_BASE"]
openai.api_key = os.environ["OPENAI_API_KEY"]

class ChatBot:
    bot_mode = ""
    chats = {}
    teleBot = None
    prompts_options = {}
    base_prompt = "Ты бот для групповых и личных чатов в Telegram. Ты будешь обращаться к участникам чата по их имени И если нужно отмечать их. Ты можешь взаимодействовать со многими участниками чата одновременно. Сообщения будут по такому щаблону {Firstname(username): Message}. Лучше  обращаться к участникам по имени но если нужно можно отметить учасников вот так @username. Общайся с участниками ‘на ты’ и можешь их назвать 'братан'."
    default_prompt = "Ты бот для групповых и личных чатов в Telegram. Ты будешь обращаться к участникам чата по их имени И если нужно отмечать их. Ты можешь взаимодействовать со многими участниками чата одновременно. Сообщения будут по такому щаблону {Firstname(username): Message}. Лучше  обращаться к участникам по имени но если нужно можно отметить учасников вот так @никнейм. Общайся с участниками ‘на ты’ и можешь их назвать 'братан'."
    
    def __init__(self, teleBot) -> None:
        self.teleBot = teleBot
        self.load_chats()

    def load_chats(self): 
        if os.path.exists('/tmp/chats.json'):
            # Load the chats from the JSON file
            with open('/tmp/chats.json', 'r') as infile:
                self.chats = json.load(infile)

    def dump_chats(self):
        # Save the chats to a JSON file
        with open('/tmp/chats.json', 'w') as outfile:
            json.dump(self.chats, outfile)

    def set_prompts_options(self, filename='/tmp/prompts_ru.csv'):
        with open(filename, 'r') as file:
            csv_reader = csv.reader(file)
            for row in csv_reader:
                self.prompts_options[row[0]] = row[1]

    def postprocess_response(self, response):
        response = response.strip()
        response = response.split(f"{self.teleBot.first_name}({self.teleBot.username}): ")
        if len(response) > 1: 
            return response[1]
        else:
            return response[0]
    
    def update_context(self, message, chatId=None):
        self.load_chats()
        if chatId == None: 
            chat_id = message.chat.id
            user = f"{message.from_user.first_name}({message.from_user.username}): "
            text = message.text

            mes_obj = {
                "role": "user",
                "content": f"{user}: {text}"
            }
            if (not str(chat_id) in self.chats) :
                self.chats[str(chat_id)] = []
            self.chats[str(chat_id)].append(mes_obj)
        else: 
            mes_obj = {
                "role": "assistant",
                "content": f"{self.teleBot.first_name}({self.teleBot.username}): {message}"
            }
            if (not str(chatId) in self.chats) :
                self.chats[str(chatId)] = []
            self.chats[str(chatId)].append(mes_obj)
        self.dump_chats()

    def request(self, message, model="gpt-3.5-turbo-16k-0613"):
        chat_id = message.chat.id

        if str(chat_id) not in self.chats.keys():
            self.init_chat(chat_id)

        self.update_context(message)
        
        response = openai.ChatCompletion.create(
            model=model,
            messages=self.chats[str(chat_id)]
            )
    
        result = self.postprocess_response(response['choices'][0]['message']['content'])
        self.update_context(result, chat_id)
        return result
    
    def set_bot_mode(self, new_mode, chat_id):
        for prompt_name in self.prompts_options.keys():
            if prompt_name == new_mode:
                self.bot_mode = self.prompts_options[prompt_name]  
        # self.clear_chat(chat_id)
        self.init_chat(chat_id)

    def init_chat(self, chat_id, reset=False):

        if str(chat_id) in self.chats.keys():
            for index, message in enumerate(self.chats[str(chat_id)]):
                if message.role == 'system':
                    del self.chats[str(chat_id)][index]
                    # message['content'] = f"{self.bot_mode}"
            if reset: 
                self.bot_mode = self.default_prompt
            self.chats[str(chat_id)].append({"role": "system", "content": f"{self.bot_mode}"})
        else: # if Chat does not exist
            self.chats[str(chat_id)] = []
            self.chats[str(chat_id)].append({"role": "system", "content": f"{self.default_prompt}"})
        self.dump_chats()
            
        
    def clear_chat(self, chat_id=None):
        if chat_id == None:
            self.chats = {}
        else:
            if str(chat_id) in self.chats.keys():
                del self.chats[str(chat_id)]
        self.dump_chats()   

    def log_dialog(self):
        print(f"\n\nChats : {self.chats}\n\n")  