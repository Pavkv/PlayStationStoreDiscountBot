import schedule
import time
import sqlite3 as sl
import requests as req
from bs4 import BeautifulSoup as bs
import re


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
                    DiscountedUntil = txt[1]
                    continue
            if DiscountPrice == BasePrice and DiscountPrice == PlusPrice:
                DiscountPrice = 0
                DiscountedUntil = 0
            cur = ps_games.cursor()
            cur.execute('''UPDATE GAMES SET Discount_Price = ? WHERE Game_Name = ?''', (DiscountPrice, GameName))
            cur.execute('''UPDATE GAMES SET Discounted_Until = ? WHERE Game_Name = ?''', (DiscountedUntil, GameName))
            ps_games.commit()
    with ps_games:
        data = ps_games.execute("SELECT Game_Name FROM GAMES WHERE Discount_price != 0")
        for game in data:
            print(''.join(game) + ' is now on sale')


schedule.every(1).seconds.do(check)
# schedule.every().day.at('00:03').do(check)
while True:
    schedule.run_pending()
    time.sleep(1)