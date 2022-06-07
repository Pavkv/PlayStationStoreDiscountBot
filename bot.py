#!/usr/bin/env python
# -*- coding: utf-8 -*-
#imports
import json
import sqlite3 as sl
import requests as req
import telebot as tb
from telebot import types
from apscheduler.schedulers.blocking import BlockingScheduler


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
    Game = collect_game_data(check_game_name(game))
    ps_games = sl.connect('ps_store_discounts.db')
    with ps_games:
        data = ps_games.execute("SELECT Game_Name FROM GAMES")
        for game1 in data:
            if game1[0] == Game[0]:
                return 'Game already existed'
    sql = 'INSERT INTO GAMES (Game_Name, Base_Price) values(?, ?)'
    base = [(Game[0], Game[1])]
    with ps_games:
        ps_games.executemany(sql, base)
        return 'Your game was successfully added'


def delete(game):
    ps_games = sl.connect('ps_store_discounts.db')
    with ps_games:
        data = ps_games.execute("SELECT Game_Name FROM GAMES")
        for d in data:
            if game.lower().__contains__(str(d).lower()) \
                    or str(d).lower().__contains__(game.lower()):
                sql = 'DELETE FROM GAMES WHERE Game_Name = ?'
                cur = ps_games.cursor()
                cur.execute(sql, (d[0],))
                ps_games.commit()
                return 'Your game was successfully delete'
    return 'There is no such game'


def check():
    ps_games = sl.connect('ps_store_discounts.db')
    string = ''
    with ps_games:
        data = ps_games.execute("SELECT Game_Name FROM GAMES")
        for game in data:
            Game = check_game_name(game[0])
            if Game['formattedBasePrice'] != Game['formattedSalePrice']:
                string += f'{Game["ProductName"]} is on sale until {Game["DiscountedUntil"]} for {Game["formattedSalePrice"]}/{Game["formattedBasePrice"]}\n'
    if string:
        return string
    else:
        return 'There is no discount'


class User:
    def __init__(self, _user, _user_id):
        self.user = _user
        self.user_id = _user_id

    def check_user(self):
        ps_ids = sl.connect('ps_store_discounts.db')
        with ps_ids:
            data = ps_ids.execute("SELECT user_id FROM USER_IDS")
            for id in data:
                if id == self.user_id:
                    return
            sql = 'INSERT INTO USER_IDS (user_id, user_name) values(?, ?)'
            base = [(self.user_id, self.user)]
            with ps_ids:
                ps_ids.executemany(sql, base)
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
        ps_ids = sl.connect('ps_store_discounts.db')
        with ps_ids:
            data = ps_ids.execute("SELECT user_id FROM USER_IDS")
            for id in data:
                bot.send_message(id[0], check())

    scheduler.add_job(check_discount, 'cron', day_of_week='mon', timezone='US/Eastern', hour=13)
    scheduler.start()

    bot.enable_save_next_step_handlers(delay=2)
    bot.load_next_step_handlers()
    bot.polling()


main()

