import sqlite3

connection = sqlite3.connect("app.db")
cursor = connection.cursor()
cursor.execute("""INSERT INTO stock (id,symbol, name, exchange) VALUES
                (1,'AAPL', 'Apple', 'NASDAQ'),
                (2,'TSLA', 'Tesla', 'NASDAQ'),
                (3,'MSFT', 'Microsoft', 'NASDAQ'),
                (4,'AMZN', 'Amazon', 'NASDAQ'),
                (5,'GME', 'GameStop', 'NYSE'),
                (6,'AMC', 'AMC Entertainment Holdings', 'NYSE'),
                (7,'NVDA', 'NVIDIA Corporation', 'NASDAQ'),
                (8,'FB', 'Meta Platforms ', 'NASDAQ'),
                (9,'GOOGL', 'Alphabet Inc ClassA ', 'NASDAQ'),
                (10,'JPM', 'JPMorgan Chase', 'NYSE'),
                (11,'DKNG', 'Draftkings Inc', 'NASDAQ'),
                (12,'NIO', 'Nio ', 'NYSE'),
                (13,'NFLX', 'Netflix ', 'NASDAQ'),
                (14,'PYPL', 'Paypal Holdings ', 'NASDAQ'),
                (15,'SHOP', 'Shopify ', 'NYSE'),
                (16,'SQ', 'Block', 'NYSE'),
                (17,'PLTR', 'Palantir Technologies', 'NYSE'),
                (18,'ARKK', 'ARK Innovation ETF', 'NYSEARCA'),
                (19,'HOOD', 'RobinHood Markets', 'NASDAQ'),
                (20,'MRNA', 'Moderna', 'NASDAQ'),
                (21,'PFE', 'Pfizer', 'NYSE'),
                (22,'NET', 'Cloudflare', 'NYSE'),
                (23,'NKE', 'Nike', 'NYSE'),
                (24,'AMD', 'Advanced Micro Devices', 'NASDAQ'),
                (25,'ETSY', 'Etsy', 'NASDAQ'),
                (26,'COIN', 'Coinbase', 'NASDAQ'),
                (27,'FVRR', 'Fiverr International', 'NYSE'),
                (28,'DWAC', 'Digital World Acquisition Corp', 'NASDAQ'),
                (29,'ROKU', 'Roku Inc', 'NASDAQ'),
                (30,'SPY', 'SPDR S&P 500 ETF Trust', 'NYSEARCA'),
                (31,'RIVN', 'Rivian Automotive', 'NASDAQ'),
                (32,'ENPH', 'Enphase Energy', 'NASDAQ'),
                (33,'AFRM', 'Affirm Holdings', 'NASDAQ'),
                (34,'WFC', 'Wells Fargo & Co', 'NYSE'),
                (35,'BABA', 'Alibaba Group Holding', 'NYSE')

""")
connection.commit()