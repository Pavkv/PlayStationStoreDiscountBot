import requests as req
from bs4 import BeautifulSoup as bs
import re
import sqlite3 as sl


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