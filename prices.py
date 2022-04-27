import sqlite3, config
from datetime import date, datetime, timedelta
import datetime
import pytz
import time
import schedule
from alpaca_trade_api.rest import REST, TimeFrame, TimeFrameUnit

def get_price_data():
    connection = sqlite3.connect('app.db')
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cursor.execute("""
            SELECT id, symbol, name FROM stock
        """)
    rows = cursor.fetchall()
    #needed to avoid repeated rows
    cursor.execute("""
            DELETE FROM stock_price
        """)

    symbols = []
    stock_dict = {}#to store the symbol and row[id] that corresponds to the symbol
    for row in rows:
        symbol = row['symbol']
        symbols.append(symbol)
        stock_dict[symbol] = row['id']
            
    api =REST(config.API_KEY, config.SECRET_KEY, base_url=config.BASE_URL, api_version='v2')

    chunk_size = 10
    for i in range(0, len(symbols), chunk_size):
        symbol_chunk = symbols[i:i+chunk_size]
        market_timezone = pytz.timezone('Europe/London') 
        start_dt = datetime.datetime.today() - datetime.timedelta(days=1)
        start = market_timezone.localize(start_dt).isoformat()
        barsets = api.get_bars(symbol_chunk,TimeFrame(5, TimeFrameUnit.Minute),start = start)._raw
        
        for bar in barsets:
            symbol = bar["S"]
            print(f"processing symbol {symbol}")
            stock_id = stock_dict[bar["S"]]
            cursor.execute("""
            INSERT INTO stock_price (stock_id, date, open, high, low, close, volume)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (stock_id, bar["t"], bar["o"], bar["h"], bar["l"], bar["c"], bar["v"]))
            
            connection.commit()

schedule.every(60).seconds.do(get_price_data)

get_price_data()
while True:
    schedule.run_pending()
    time.sleep(1)
