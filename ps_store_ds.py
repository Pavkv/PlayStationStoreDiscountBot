def add(game):
    import requests as req
    from bs4 import BeautifulSoup as bs
    import re
    import sqlite3 as sl
    import sys

    ps_games = sl.connect('ps_store_discounts.db')
    game = str(input("Write name of a game: "))
    game = re.sub(r"\s+", '', game)
    url = 'https://platprices.com/api.php?key=4SGYBOeNA7S2ADj4rBaolWhRPQkrw1pK&name=' + game + '&region=ru'
    count = False
    resp = req.get(url)
    soup = bs(resp.text, 'lxml')
    text = str(soup.body).split(',')
    if not text:
        print('Incorrect Game name, please write again')
        sys.exit(0)
    for txt in text:
        if txt.__contains__("Game/product not found."):
            print('Incorrect Game name, please write again')
            sys.exit(0)
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
    if DiscountPrice == BasePrice or DiscountPrice == PlusPrice:
        DiscountPrice = 0
        DiscountedUntil = 0
    with ps_games:
        data = ps_games.execute("SELECT Game_Name FROM GAMES")
        for d in data:
            if game.lower().__contains__(str(d[0]).lower()) or str(d[0]).lower().__contains__(game.lower()):
                count = True
    if not count:
        sql = 'INSERT INTO GAMES (Game_Name, Base_Price, Plus_Price, Discount_Price, Discounted_Until) values(?, ?, ?, ?, ?)'
        data = [
            (GameName, BasePrice, PlusPrice, 0, 0)
        ]
        with ps_games:
            ps_games.executemany(sql, data)
    else:
        with ps_games:
            cur = ps_games.cursor()
            cur.execute('''UPDATE GAMES SET Discount_Price = ? where Game_Name = ?''', (DiscountPrice, GameName))
            cur.execute('''UPDATE GAMES SET Discounted_Until = ? where Game_Name = ?''', (DiscountedUntil, GameName))
            ps_games.commit()