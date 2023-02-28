import telebot, openai, os

openai.api_key = os.environ.get("OPENAI_API_KEY")

def getText(text):
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=text,
        temperature=1, # controls the level of randomness in the generated text. A higher temperature value will produce more diverse and creative responses, while a lower value will produce more predictable responses.
        max_tokens=256, 
        top_p=1.0,
        stop=None,
        frequency_penalty=1, # encourages the model to avoid using the same words or phrases too often in the generated text. This can help make the conversation feel more varied and interesting.
        presence_penalty=1 # encourages the model to avoid repeating phrases or concepts that have already been mentioned in the conversation.This can help make the conversation feel more natural and less repetitive.
    )
    return response["choices"][0]["text"]

token = os.environ.get("BOTFATHER_API_KEY")
bot = telebot.TeleBot(token)

@bot.message_handler(commands=['start'])
def start_message(message):
    bot.reply_to(message, "Здравствуйте букашки!")

@bot.message_handler(content_types='text')
def sender(message):
    bot.reply_to(message, getText(message.text))

@bot.message_handler(commands=['stop'])
def stop_bot(message):
    print("Stop function here !!!")
    bot.reply_to(message, "Я уйду, но вы об этом скоро пожелеете!")
    bot.stop_polling()

bot.polling()




