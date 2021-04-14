import telebot as tb
from telebot import types
from ps_store_ds import add, delete, check
import schedule
import time
from multiprocessing.context import Process
from flask import Flask, request
import os
TOKEN = '1758515314:AAEqq2SHa68K51OZpbhMkxCNvayrK9ORPdg'
bot = tb.TeleBot(TOKEN)


server = Flask(__name__)


@server.route('/' + TOKEN, methods=['POST'])
def getMessage():
    json_string = request.get_data().decode('utf-8')
    update = bot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200


@server.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url='https://your_heroku_project.com/' + TOKEN)
    return "!", 200


if __name__ == "__main__":
    server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))

user_dict = {}


class User:
    def __init__(self, login):
        self.login = login


@bot.message_handler(commands=['start', 'help'])
def menu(message):
    bot.send_message(message.chat.id, 'Welcome to your ps games discount bot')
    msg = bot.reply_to(message, 'Write your login')
    bot.register_next_step_handler(msg, process_name_step)


def process_name_step(message):
    try:
        chat_id = message.chat.id
        login = message.text
        user = User(login)
        user_dict[chat_id] = user
        msg = bot.reply_to(message, 'Write your password')
        start_menu = types.ReplyKeyboardMarkup(row_width=1)
        fk = types.KeyboardButton(text='Add new game')
        sk = types.KeyboardButton(text='Delete game')
        start_menu.add(fk, sk)
        msg = bot.reply_to(message, 'What you want to do?', reply_markup=start_menu)
    except Exception as e:
        bot.reply_to(message, 'Try again')


def choose_button(message):
    try:
        if message.text == 'Add new game':
            msg = bot.reply_to(message, 'Write game name')
            bot.register_next_step_handler(msg, add_new_game)
        elif message.text == 'Delete game':
            msg = bot.reply_to(message, 'Write game name')
            bot.register_next_step_handler(msg, delete_game)
    except Exception as e:
        bot.reply_to(message, 'Try again')


def add_new_game(message):
    try:
        if message.text:
            game = str(message.text)
            bot.reply_to(message, add(game))
    except Exception as e:
        bot.reply_to(message, 'Try again')


def delete_game(message):
    try:
        if message.text:
            game = str(message.text)
            bot.reply_to(message, delete(game))
    except Exception as e:
        bot.reply_to(message, 'Try again')


def send_message1():
    bot.send_message(432131247, check())


schedule.every().day.at('00:03').do(send_message1)


class ScheduleMessage():
    def try_send_schedule():
        while True:
            schedule.run_pending()
            time.sleep(1)

    def start_process():
        p1 = Process(target=ScheduleMessage.try_send_schedule, args=())
        p1.start()


if __name__ == '__main__':
    ScheduleMessage.start_process()
    try:
        bot.polling(none_stop=True)
    except:
        pass


bot.enable_save_next_step_handlers(delay=2)
bot.load_next_step_handlers()