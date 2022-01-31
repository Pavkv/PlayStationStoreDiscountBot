import requests as req
import re
import sqlite3 as sl
import json


def collect_game_data(data):
    GameName = data['GameName']
    BasePrice = data['formattedBasePrice']
    PlusPrice = data['formattedPlusPrice']
    DiscountPrice = data['formattedSalePrice']
    DiscountedUntil = data['DiscountedUntil']
    if DiscountPrice == BasePrice or DiscountPrice == PlusPrice:
        DiscountPrice = 0
        DiscountedUntil = 0
    return GameName, BasePrice, PlusPrice, DiscountPrice, DiscountedUntil


def check_game_name(game):
    url = 'https://platprices.com/api.php?key=4SGYBOeNA7S2ADj4rBaolWhRPQkrw1pK&name=' + game + '&region=ru'
    resp = req.get(url)
    data = json.loads(resp.text)
    if not data:
        return 'Incorrect Game name, please write again'
    elif data['error'] == 3:
        return 'Game was not found'
    else:
        return data


def add(game):
    if type(check_game_name(game)) == dict:
        GameName, BasePrice, PlusPrice, DiscountPrice, DiscountedUntil = collect_game_data(check_game_name(game))
    else:
        return check_game_name(game)
    ps_games = sl.connect('ps_store_discounts.db')
    count = False
    with ps_games:
        data = ps_games.execute("SELECT Game_Name FROM GAMES")
        game1 = re.sub(r"\s+", '', game)
        for d in data:
            if game.lower().__contains__(str(d[0]).lower()) or str(d[0]).lower().__contains__(game.lower())\
                    or game1.lower().__contains__(str(d[0]).lower()) or str(d[0]).lower().__contains__(game1.lower()):
                count = True
                return 'Game already existed'
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
            if type(check_game_name(game)) == dict:
                GameName, BasePrice, PlusPrice, DiscountPrice, DiscountedUntil = collect_game_data(
                    check_game_name(game))
            else:
                return check_game_name(game)
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

game = "Uncharted: Legacy of Thieves"
print(add(game))