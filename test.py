import matplotlib.pyplot as plt
import sqlite3
import pandas as pd
import plotly
import plotly.express as px
import datetime
from datetime import date
import time
from alpaca_trade_api.rest import TimeFrame, REST
import numpy as np

import config 
connection = sqlite3.connect('app.db')
connection.row_factory = sqlite3.Row
cursor = connection.cursor()

sentiment = """ SELECT COUNT(Text),Sentiment FROM tweets  WHERE Timestamp = "2022-04-13 13:01:00" group by Sentiment; """

df1 = pd.read_sql(sentiment, sqlite3.connect("app.db"))


print(df1)
#FOR MAIN.PY, could have done it all in one query but if a stock didnt have all 3 types of sentiment(positive, negative and neutral) then it lead to index errors in the dataframe since there would be a missing row.