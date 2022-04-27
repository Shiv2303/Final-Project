import json
from tweepy.streaming import Stream
from tweepy import OAuthHandler
from datetime import datetime
import tweepy
import sqlite3
import re
import config
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

connection = sqlite3.connect("app.db", timeout=30)
connection.row_factory = sqlite3.Row
cursor = connection.cursor()

cursor.execute("""
            SELECT '$'|| symbol as symbols FROM stock as symbol
            """)
rows = cursor.fetchall()
ticker_symbol=[]
for row in rows:
    symbol = row['symbols']
    ticker_symbol.append(symbol)


class MyStreamListener(Stream):
    def on_status(self, status):
        # Load the Tweet into the variable "t"
        t = status._json
        # Pulls data from the tweet to store in the database.
        Text = t["text"]  # The entire body of the Tweet
        if (status.retweeted or "RT @" in status.text):  # removes any retweets to avoid repeated data
            return
        if("discord" in status.text): # tweets that have'discord' in them will be ignored
            return
        if ( status.truncated):  # needed to get full text, without this the text as capped at 140 charchters so if there are more than 140 charchters can now get the full text
            Text = status.extended_tweet["full_text"]
        else:
            Text = status.text
        
        
        Text = re.sub(r"https?:\/\/\S+", "", Text)  # removes any URL from tweets
        Text = re.sub("[#]", "", Text)  # remove '#' from tweets
        Text = re.sub("[$]", "", Text)  # remove '$' from tweets
        Text = re.sub(r"@[A-Za-z0-9]+","",Text)# removes @
        Time = t["created_at"]  # The timestamp of when the Tweet was created
        Timestamp = datetime.strftime(datetime.strptime(Time, "%a %b %d %H:%M:%S +0000 %Y"),"%Y-%m-%d %H:%M:%S")# converts timestamp from Sun Jan 2 10:55:12 +0000 2022 format to yyy



        Follower_Count = t["user"]["followers_count"] #get follower count of user tweeting
       
        #sentiment analysis
        analysis = SentimentIntensityAnalyzer()
        Polarity = analysis.polarity_scores(Text)["compound"]
        if Polarity <= -0.05:
            Sentiment = "Negative"
        elif Polarity >= 0.05:
            Sentiment = "Positive"
        else:
            Sentiment = "Neutral"   
        # Insert data into the database
        tsymbol = [symbol.replace('$', '')for symbol in ticker_symbol] 
        for word in tsymbol:
            if word in Text:
                # Insert data into the database
                cursor.execute(
                """INSERT INTO tweets(ticker, Timestamp, Text, Polarity,Sentiment, Follower_Count) VALUES(?,?,?,?,?,?)""",
                (word,Timestamp, Text, Polarity, Sentiment,Follower_Count ))
                connection.commit()
                
            else:
                None    
        return True


# api keys
myStreamListener_new = MyStreamListener(
    config.consumer_key,
    config.consumer_secret,
    config.access_token,
    config.access_token_secret
)
myStreamListener_new.filter(
    track= ticker_symbol, languages=["en"]
)  # filter data and only retrive what is needed