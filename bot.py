#!/usr/bin/env python
# -*- coding: utf-8 -*-
import telebot as tb
from telebot import types
import schedule
import time
from multiprocessing.context import Process
import requests as req
from bs4 import BeautifulSoup as bs
import re
import sqlite3 as sl

TOKEN = '1758515314:AAEqq2SHa68K51OZpbhMkxCNvayrK9ORPdg'
bot = tb.TeleBot(TOKEN)

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
    bot.send_message(432131247, check)


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
bot.polling()


def add(game):
    ps_games = sl.connect('ps_store_discounts.db')
    url = 'https://platprices.com/api.php?key=4SGYBOeNA7S2ADj4rBaolWhRPQkrw1pK&name=' + game + '&region=ru'
    count = False
    resp = req.get(url)
    soup = bs(resp.text, 'lxml')
    text = str(soup.body).split(',')
    with ps_games:
        data = ps_games.execute("SELECT Game_Name FROM GAMES")
        game1 = re.sub(r"\s+", '', game)
        for d in data:
            if game.lower().__contains__(str(d[0]).lower()) or str(d[0]).lower().__contains__(game.lower())\
                    or game1.lower().__contains__(str(d[0]).lower()) or str(d[0]).lower().__contains__(game1.lower()):
                count = True
                return 'Game already existed'
    if not text:
        return 'Incorrect Game name, please write again'
    for txt in text:
        if txt.__contains__("Game/product not found."):
            return 'Game was not found'
    for txt in text:
        txt = re.sub(r'"', '', txt)
        if txt.__contains__('GameName'):
            txt = txt.split(':')
            GameName = txt[1]
            continue
        elif txt.__contains__('formattedBasePrice'):
            txt = txt.split(':')
            BasePrice = txt[1]
            continue
        elif txt.__contains__('formattedPlusPrice'):
            txt = txt.split(':')
            PlusPrice = txt[1]
            continue
    if not count:
        sql = 'INSERT INTO GAMES (Game_Name, Base_Price, Plus_Price, Discount_Price, Discounted_Until) values(?, ?, ?, ?, ?)'
        data = [
            (GameName, BasePrice, PlusPrice, 0, 0)
        ]
        with ps_games:
            ps_games.executemany(sql, data)
            return 'Your game was successfully added'


def delete(game):
    ps_games = sl.connect('ps_store_discounts.db')
    with ps_games:
        data = ps_games.execute("SELECT Game_Name FROM GAMES")
        for d in data:
            if game.lower().__contains__(str(d[0]).lower()) or str(d[0]).lower().__contains__(game.lower()):
                cur = ps_games.cursor()
                cur.execute('''DELETE FROM GAMES WHERE Game_Name = ?''', (game,))
                ps_games.commit()
        return 'Your game was successfully delete'


def check():
    ps_games = sl.connect('ps_store_discounts.db')
    with ps_games:
        data = ps_games.execute("SELECT Game_Name FROM GAMES")
        for game in data:
            url = 'https://platprices.com/api.php?key=4SGYBOeNA7S2ADj4rBaolWhRPQkrw1pK&name=' + ''.join(game) + '&region=ru'
            resp = req.get(url)
            soup = bs(resp.text, 'lxml')
            text = str(soup.body).split(',')
            for txt in text:
                txt = re.sub(r'"', '', txt)
                if txt.__contains__('GameName'):
                    txt = txt.split(':')
                    GameName = txt[1]
                    continue
                elif txt.__contains__('formattedBasePrice'):
                    txt = txt.split(':')
                    BasePrice = txt[1]
                    continue
                elif txt.__contains__('formattedPlusPrice'):
                    txt = txt.split(':')
                    PlusPrice = txt[1]
                    continue
                elif txt.__contains__('formattedSalePrice'):
                    txt = txt.split(':')
                    DiscountPrice = txt[1]
                    continue
                elif txt.__contains__('DiscountedUntil'):
                    txt = txt.split(':')
                    du = txt[1]
                    du = du.split(' ')
                    DiscountedUntil = du[0]
                    continue
            if DiscountPrice == BasePrice and DiscountPrice == PlusPrice:
                DiscountPrice = 0
                DiscountedUntil = 0
            cur = ps_games.cursor()
            cur.execute('''UPDATE GAMES SET Discount_Price = ? WHERE Game_Name = ?''', (DiscountPrice, GameName))
            cur.execute('''UPDATE GAMES SET Discounted_Until = ? WHERE Game_Name = ?''', (DiscountedUntil, GameName))
            ps_games.commit()
    with ps_games:
        data1 = ps_games.execute("SELECT Game_Name FROM GAMES WHERE Discount_price != 0")
        data2 = ps_games.execute("SELECT Discount_price FROM GAMES WHERE Discount_price != 0")
        data3 = ps_games.execute("SELECT Discounted_Until FROM GAMES WHERE Discount_price != 0")
        if data:
            s = ''
            for game1, game2, game3 in zip(data1, data2, data3):
                s += ''.join(game1) + ' - ' + ''.join(game2) + ' - ' + ''.join(game3) + '\n'
            if data1.rowcount == 1:
                return 'Is now on sale: ' + s
            else:
                return 'Are now on sales: ' + s