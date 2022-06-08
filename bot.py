import json
# import sqlite3 as sl
import os
import psycopg2 as pg
import requests as req
import telebot as tb
from telebot import types
from apscheduler.schedulers.blocking import BlockingScheduler
database_url = os.environ.get('jdbc:postgresql://ec2-54-165-178-178.compute-1.amazonaws.com:5432/dfoviovij8dqfv')


def collect_game_data(data):
    Game = [data['ProductName'], data['formattedBasePrice']]
    return Game


def check_game_name(game):
    url = 'https://platprices.com/api.php?key=4SGYBOeNA7S2ADj4rBaolWhRPQkrw1pK&name=' + game
    resp = req.get(url)
    data = json.loads(resp.text)
    if not data:
        return 'Incorrect Game name, please write again'
    elif data['error'] == 3:
        return 'Game was not found'
    else:
        return data


def add(game):
    ps_games = pg.connect(database_url)
    cur = ps_games.cursor()
    Game = collect_game_data(check_game_name(game))
    data = cur.execute("SELECT Game_Name FROM games")
    for game1 in data:
        if game1[0] == Game[0]:
            return 'Game already existed'
    sql = 'INSERT INTO GAMES (Game_Name, Base_Price) values(?, ?)'
    base = [(Game[0], Game[1])]
    cur.execute(sql, base)
    ps_games.close()
    return 'Your game was successfully added'


def delete(game):
    ps_games = pg.connect(database_url)
    cur = ps_games.cursor()
    data = cur.execute("SELECT Game_Name FROM games")
    for d in data:
        if game.lower().__contains__(str(d).lower()) \
                or str(d).lower().__contains__(game.lower()):
            sql = 'DELETE FROM GAMES WHERE Game_Name = ?'
            cur.execute(sql, (d[0],))
            ps_games.commit()
            ps_games.close()
            return 'Your game was successfully delete'
    ps_games.close()
    return 'There is no such game'


def check():
    ps_games = pg.connect(database_url)
    cur = ps_games.cursor()
    string = ''
    data = cur.execute("SELECT Game_Name FROM games")
    for game in data:
        Game = check_game_name(game[0])
        if Game['formattedBasePrice'] != Game['formattedSalePrice']:
            string += f'{Game["ProductName"]} is on sale until {Game["DiscountedUntil"]} for {Game["formattedSalePrice"]}/{Game["formattedBasePrice"]}\n'
    ps_games.close()
    if string:
        return string
    else:
        return 'There is no discount'


class User:
    def __init__(self, _user, _user_id):
        self.user = _user
        self.user_id = _user_id

    def check_user(self):
        ps_games = pg.connect(database_url)
        cur = ps_games.cursor()
        data = cur.execute("SELECT user_id FROM USER_IDS")
        for id in data:
            if id == self.user_id:
                return
        sql = 'INSERT INTO USER_IDS (user_id, user_name) values(?, ?)'
        base = [(self.user_id, self.user)]
        cur.executemany(sql, base)
        ps_games.close()
        return


def main():
    TOKEN = '1758515314:AAEqq2SHa68K51OZpbhMkxCNvayrK9ORPdg'
    bot = tb.TeleBot(TOKEN)

    @bot.message_handler(commands=['start', 'help'])
    def menu(message):
        bot.send_message(message.chat.id, 'Welcome to your ps games discount bot')
        msg = bot.reply_to(message, 'Write your login')
        bot.register_next_step_handler(msg, process_name_step)

    def process_name_step(message):
        try:
            user = User(message.from_user.first_name + message.from_user.last_name, message.chat.id)
            user.check_user()
            start_menu = types.ReplyKeyboardMarkup(row_width=1)
            add_game = types.KeyboardButton(text='Add new game')
            delete_game = types.KeyboardButton(text='Delete game')
            check_discount = types.KeyboardButton(text='Check discount')
            start_menu.add(add_game, delete_game, check_discount)
            bot.reply_to(message, 'What you want to do?', reply_markup=start_menu)
        except Exception as e:
            bot.reply_to(message, 'Try again')

    @bot.message_handler(content_types=["text"])
    def choose_button(message):
        try:
            if message.text == 'Add new game':
                msg = bot.reply_to(message, 'Write game name')
                bot.register_next_step_handler(msg, add_new_game)
            elif message.text == 'Delete game':
                msg = bot.reply_to(message, 'Write game name')
                bot.register_next_step_handler(msg, delete_game)
            elif message.text == 'Check discount':
                bot.reply_to(message, check())
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

    scheduler = BlockingScheduler()

    def check_discount():
        ps_games = pg.connect(database_url)
        cur = ps_games.cursor()
        data = cur.execute("SELECT user_id FROM USER_IDS")
        for id in data:
            bot.send_message(id[0], check())
        ps_games.close()

    scheduler.add_job(check_discount, 'cron', day_of_week='mon', timezone='US/Eastern', hour=13)
    scheduler.start()

    bot.enable_save_next_step_handlers(delay=2)
    bot.load_next_step_handlers()
    bot.polling()


main()
