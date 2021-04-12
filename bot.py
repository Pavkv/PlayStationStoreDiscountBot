import telebot as tb
from telebot import types
from ps_store_ds import add
bot = tb.TeleBot('1758515314:AAEqq2SHa68K51OZpbhMkxCNvayrK9ORPdg')

user_dict = {}

class User:
    def __init__(self, login):
        self.login = login
        self.password = None


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
        bot.register_next_step_handler(msg, process_password_step)
    except Exception as e:
        bot.reply_to(message, 'Try again')


def process_password_step(message):
    try:
        chat_id = message.chat.id
        password = message.text
        user = User(password)
        user_dict[chat_id] = user
        start_menu = types.ReplyKeyboardMarkup(row_width=1)
        fk = types.KeyboardButton(text='Add new game')
        sk = types.KeyboardButton(text='Delete game')
        start_menu.add(fk, sk)
        msg = bot.reply_to(message, 'What you want to do?', reply_markup=start_menu)
    except Exception as e:
        bot.reply_to(message, 'Try again')


def add_new_game(message):
    try:
        if message.text == 'Add new game':
            bot.send_message(message.from_user.id, 'Hey')
    except Exception as e:
        bot.reply_to(message, 'Try again')


bot.enable_save_next_step_handlers(delay=2)
bot.load_next_step_handlers()
bot.polling()