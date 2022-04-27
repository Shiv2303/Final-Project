import sqlite3
connection = sqlite3.connect("app.db")
cursor = connection.cursor()

cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS stock (
        id INTEGER,
        symbol TEXT NOT NULL UNIQUE, 
        name TEXT NOT NULL,
        exchange TEXT NOT NULL,
        PRIMARY KEY(id, symbol)

    )
"""
)
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS stock_price (
        id INTEGER, 
        stock_id INTEGER,
        date  NOT NULL,
        open NOT NULL, 
        high NOT NULL, 
        low NOT NULL, 
        close NOT NULL, 
        volume NOT NULL,
        PRIMARY KEY(id),
        FOREIGN KEY (stock_id) REFERENCES stock (id)
    )
"""
)


cursor.execute(
    """ 
    CREATE TABLE IF NOT EXISTS tweets(
    "id"	Integer,
	"ticker"	TEXT,
	"Timestamp"	TIMESTAMP NOT NULL,
	"Text"	TEXT NOT NULL,
	"Polarity"	INTEGER NOT NULL,
	"Sentiment"	TEXT NOT NULL,
	FOREIGN KEY("ticker") REFERENCES "stock"("symbol"),
	FOREIGN KEY("Timestamp") REFERENCES "stock_price"("date"),
	PRIMARY KEY("id")

    )
"""
)
connection.commit()


