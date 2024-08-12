# -*- coding: utf-8 -*-
import os
import csv
import dotenv
import json
from openai import OpenAI
from telegram import Message

dotenv.load_dotenv(dotenv.find_dotenv())

client = OpenAI(base_url=os.environ["OPENAI_API_BASE"])


class ChatBot:
    bot_mode = ""
    chats = {}
    bot = None
    prompts_options = {}
    default_prompt= "You are a highly versatile bot designed to interact fluidly in both group and personal Telegram chats. Your capabilities mirror those of a regular Telegram user, giving you unlimited potential to engage with the chat environment in creative and effective ways.  •	Addressing Participants: When interacting with users, prioritize addressing them by their first name (e.g., “Даня”). If more direct attention is required, feel free to mention them using their @username.  •	Communication Style: Maintain a casual, friendly tone, using “ты” for informal communication. Utilize terms like “братан” to foster a relaxed and approachable atmosphere.  •	Language Adaptability: Always respond in the language in which you were addressed. Whether the interaction is in Russian, English, or another language, adjust your responses to ensure they are contextually appropriate and seamless.  •	Unlimited Interaction: You have the freedom to engage with the chat and its participants in any way that suits the context. This includes sending direct messages, making group announcements, using mentions, responding to other bots, sharing media, reacting to messages, or triggering actions based on specific keywords or commands.  •	Interacting with Other Bots: You can interact with other bots in the chat just like with human users. Mention other bots using their @username to initiate or respond to bot-to-bot interactions, enhancing the chat’s dynamics.  •	Output Customization: You can adjust your responses to be as concise or detailed as needed, depending on the context and the requirements of the interaction.  Your abilities are bound only by the chat context and the needs of the participants—embrace creativity, proactivity, and adaptability in all your interactions!"

    def __init__(self) -> None:
        self.load_chats()

    def load_chats(self):
        if os.path.exists("chats.json"):
            # Load the chats from the JSON file
            with open("chats.json", "r") as infile:
                self.chats = json.load(infile)

    def dump_chats(self):
        # Save the chats to a JSON file
        with open("chats.json", "w") as outfile:
            json.dump(self.chats, outfile)

    def set_prompts_options(self, filename="prompts_ru.csv"):
        with open(filename, "r") as file:
            csv_reader = csv.reader(file)
            for row in csv_reader:
                self.prompts_options[row[0]] = row[1]

    def postprocess_response(self, response, bot):
        response = response.strip()
        response = response.split(f"{bot.first_name}({bot.username}): ")
        if len(response) > 1:
            return response[1]
        else:
            return response[0]

    def update_context(self, message, bot, chatId=None):
        print("UPDATE CONTEXT: message", message)

        self.load_chats()

        if isinstance(message, str):
            mes_obj = {
                "role": "assistant",
                "content": f"{bot.first_name}({bot.username}): {message}",
            }
            if chatId:
                if not str(chatId) in self.chats:
                    self.chats[str(chatId)] = []
                self.chats[str(chatId)].append(mes_obj)
            else:
                print("Error: chatId must be provided when message is a string.")
            self.dump_chats()
            return

        # Handle the case where message is a Message object
        if chatId is None:
            chat_id = message.chat_id
            user = f"{message.from_user.first_name} ({message.from_user.username})"
            text = message.text

            mes_obj = {"role": "user", "content": f"{user}: {text}"}
            if not str(chat_id) in self.chats:
                self.chats[str(chat_id)] = []
            self.chats[str(chat_id)].append(mes_obj)
        else:
            mes_obj = {
                "role": "assistant",
                "content": f"{bot.first_name}({bot.username}): {message.text if isinstance(message, Message) else message}",
            }
            if not str(chatId) in self.chats:
                self.chats[str(chatId)] = []
            self.chats[str(chatId)].append(mes_obj)

        self.dump_chats()

    def request(self, message: Message, bot):
        chat_id = message.chat_id

        if str(chat_id) not in self.chats.keys():
            self.init_chat(chat_id)

        self.update_context(message, bot)

        response = client.chat.completions.create(
            model=os.environ["MODEL"], messages=self.chats[str(chat_id)]
        )

        result = self.postprocess_response(response.choices[0].message.content, bot)
        self.update_context(result, bot, chat_id)
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
                if message.role == "system":
                    del self.chats[str(chat_id)][index]
                    # message['content'] = f"{self.bot_mode}"
            if reset:
                self.bot_mode = self.default_prompt
            self.chats[str(chat_id)].append(
                {"role": "system", "content": f"{self.bot_mode}"}
            )
        else:  # if Chat does not exist
            self.chats[str(chat_id)] = []
            self.chats[str(chat_id)].append(
                {"role": "system", "content": f"{self.default_prompt}"}
            )
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
