import json
import telebot
from info import informat
from telebot import types

token = "6560339169:AAGfa974FK1i_y0-wvMhvOZP9iQBOYclx28"
bot = telebot.TeleBot(token=token)
def add_user(id,name):
    with open('data.json') as f:
        data = json.load(f)
    if str(id) in data["users"].keys():
        print()
    else:
        data['users'][str(id)] = name, False, "kr"
        with open('data.json', 'w') as outfile:
            json.dump(data, outfile, indent=2)
def sv_data(id, lvl):
    with open('data.json') as f:
        data = json.load(f)
    data['users'][str(id)][2] = lvl
    with open('data.json', 'w') as outfile:
        json.dump(data, outfile, indent=2)

@bot.message_handler(content_types = ['text'])
def vvod(message):
    add_user(message.chat.id, message.from_user.first_name)
    with open('data.json') as f:
        data = json.load(f)
    if data['users'][str(message.chat.id)][1] == False:
        if message.text == "/start" or message.text == "/help":
            bot.send_message(message.chat.id, informat(message.chat.id, message.text))
        elif message.text == "/quest":
            quest(message.chat.id)
        else:
            bot.send_message(message.chat.id, "такой команды нет")
    elif data['users'][str(message.chat.id)][1] == True:
        with open('locations.json', encoding="utf-8") as g:
            locations = json.load(g)
        if message.text in locations["locations"][data["users"][str(message.chat.id)][2]]["vpr"]:
            sv_data(str(message.chat.id), locations["locations"][data["users"][str(message.chat.id)][2]]["vpr"][message.text])
            mech(message.chat.id)
        else:
            bot.send_message(message.chat.id, "не правильно введённый выбор")

def quest(id):
    with open('data.json') as f:
        data = json.load(f)
    data['users'][str(id)][1] = True
    with open('data.json', 'w') as outfile:
        json.dump(data, outfile, indent=2)
    mech(id)
def mech(id):
    with open('data.json') as f:
        data = json.load(f)
    lvl = data["users"][str(id)][2]
    if lvl == "won" or lvl == "over":
        data['users'][str(id)][1] = False
        data['users'][str(id)][2] = "kr"
        with open('data.json', 'w') as outfile:
            json.dump(data, outfile, indent=2)
    else:
        with open('locations.json', encoding="utf-8") as g:
            locations = json.load(g)
        question = locations["locations"][lvl]["text"]
        options = locations["locations"][lvl]["vpr"]
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        for text in options:
            markup.add(text)
        h = locations["locations"][lvl]["file"]
        if ".png" in h:
            bot.send_photo(id, h)
        else:
            bot.send_video(id, h)
        bot.send_message(id, question, reply_markup=markup)
bot.polling()