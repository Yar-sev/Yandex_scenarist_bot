import telebot
from database_func import *
import logging
from info import *
from YaGPT_func import *

bot = telebot.TeleBot(token=token)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename="log_file.txt",
    filemode="w",
)
create_db()
collection = {}
texts = {}
@bot.message_handler(content_types = ['text'])
def enter(message):
    user_database(message.chat.id)
    msg = message.text.lower()
    if msg in ["/start", "/help"]:
        bot.send_message(message.chat.id, commands[msg])
        logging.info(msg)
        check(message.chat.id)
    elif msg == "/start_history":
        user_database(message.chat.id)
        if len(datafr()) == 2 and user(message.chat.id) == False:
            bot.send_message(message.chat.id, "тебе нельзя")
        else:
            if select_data(message.chat.id)[0][2] <= MAX_MODEL_TOKENS:
                bot.send_message(message.chat.id, "у вас мало токенов")
            else:
                logging.info(msg)
                scenariy(message)
    elif msg == "/whole_history":
        try:
            bot.send_message(message.chat.id, select_data(message.chat.id)[0][8])
            logging.info(msg)
        except:
            bot.send_message(message.chat.id, "вы ещё не написали историю, или произошла ошибка")

    elif msg == "/debug":
        user_database(message.chat.id)
        check(message.chat.id)
        if select_data(message.chat.id)[0][7] == "False":
            update_data(message.chat.id, "debug", "True")
            logging.info(msg + "True")
            bot.send_message(message.chat.id, "debug True")
        elif select_data(message.chat.id)[0][7] == "True":
            update_data(message.chat.id, "debug", "False")
            logging.info(msg + "False")
            bot.send_message(message.chat.id, "debug False")
    elif msg == "/tokens":
        user_database(message.chat.id)
        bot.send_message(message.chat.id, f"ваше кол-во токенов - {select_data(message.chat.id)[0][2]}")
    elif msg == "/free_tokens":
        user_database(message.chat.id)
        update_data(message.chat.id, "token",
                    select_data(message.chat.id)[0][2] + 10000)
    else:
        bot.send_message(message.chat.id, "Я не понимаю команду")

def check(id):
    if select_data(id)[0][7] == "False":
        return None
    elif select_data(id)[0][7] == "True":
        with open("log_file.txt", "rb") as f:
            bot.send_document(id, f)

def scenariy(message):
    markup = set(information["character"])
    bot.send_message(message.chat.id, text[0], reply_markup=markup)
    logging.info("character keyboard")
    bot.register_next_step_handler(message, preprompt1)

def preprompt1(message):
    if message.text in information["character"]:
        update_data(message.chat.id, "gg", message.text)
        logging.info("save Character(gg)")
        markup = set(information["Janr"])
        bot.send_message(message.chat.id, text[1], reply_markup=markup)
        logging.info("janr keyboard")
        bot.register_next_step_handler(message, preprompt2)
    else:
        bot.send_message(message.chat.id, "такого персонажа нет в списке")
        scenariy(message)
def preprompt2(message):
    if message.text in information["Janr"]:
        update_data(message.chat.id, "Janr", message.text)
        logging.info("save Janr")
        markup = set(information["setting"])
        bot.send_message(message.chat.id, text[2], reply_markup=markup)
        logging.info("setting keyboard")
        bot.register_next_step_handler(message, preprompt3)
    else:
        bot.send_message(message.chat.id, "такого персонажа нет в списке")
        markup = set(information["Janr"])
        bot.send_message(message.chat.id, text[1], reply_markup=markup)
        bot.register_next_step_handler(message, preprompt2)
def preprompt3(message):
    if message.text in information["setting"]:
        update_data(message.chat.id, "setting", message.text)
        logging.info("save setting")
        bot.send_message(message.chat.id, text[3])
        check(message.chat.id)
        bot.register_next_step_handler(message, dop)
    else:
        bot.send_message(message.chat.id, "такого персонажа нет в списке")
        markup = set(information["setting"])
        bot.send_message(message.chat.id, text[2], reply_markup=markup)
        bot.register_next_step_handler(message, preprompt3)
def dop(message):
    msg = message.text.lower()
    if msg == "/begin":
        logging.info(msg)
        preprompt(message)
    else:
        if count_tokens(msg) <= MAX_USER_TOKEN:
            update_data(message.chat.id, "info", msg)
            logging.info("add info")
            preprompt(message)
        else:
            bot.send_message(message.chat.id, "сократи написанное")
            bot.register_next_step_handler(message, dop)

def preprompt(message):
    collection[message.chat.id] = [{'role': 'system', 'content': create_prompt(select_data(message.chat.id))}]
    logging.info("start collection")
    n = ask_gpt(collection[message.chat.id])
    texts[message.chat.id] = n
    bot.send_message(message.chat.id, n)
    bot.send_message(message.chat.id, text[4])
    logging.info("start history (not command)")
    check(message.chat.id)
    bot.register_next_step_handler(message, history)
def history(message):
    msg = message.text.lower()
    if select_data(message.chat.id)[0][2] >= MAX_MODEL_TOKENS:
        if msg == '/end':
            n = ask_gpt(collection[message.chat.id], 'end')
            texts[message.chat.id] += '\n' + n
            bot.send_message(message.chat.id, n)
            update_data(message.chat.id, "token", select_data(message.chat.id)[0][2] - count_tokens(n))
            update_data(message.chat.id, "text", texts[message.chat.id])
            texts[message.chat.id] = ""
            logging.info("end history")
            check(message.chat.id)
            bot.register_next_step_handler(message, enter)
        else:
            if count_tokens(msg) <= MAX_USER_TOKEN:
                collection[message.chat.id].append({'role': 'user', 'content': message.text})
                n = ask_gpt(collection[message.chat.id])
                texts[message.chat.id] += '\n' + n
                bot.send_message(message.chat.id, n)
                bot.send_message(message.chat.id, text[4])
                update_data(message.chat.id, "token", select_data(message.chat.id)[0][2] - count_tokens(n))
                logging.info("continuation history")
                check(message.chat.id)
                bot.send_message(message.chat.id, f"ваше кол-во токенов - {select_data(message.chat.id)[0][2]}")
                bot.register_next_step_handler(message, history)
            else:
                bot.send_message(message.chat.id, "сократи написанное")
                bot.register_next_step_handler(message, history)
    else:
        bot.send_message(message.chat.id, "у вас мало токенов")
        update_data(message.chat.id, "text", texts[message.chat.id])
        bot.send_message(message.chat.id, "история будет сохранена на данном этапе")
        texts[message.chat.id] = ""
        logging.info("end history,few tokens")
        check(message.chat.id)
        bot.register_next_step_handler(message, enter)

bot.polling()