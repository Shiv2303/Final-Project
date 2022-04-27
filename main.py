from flask import Flask, render_template, request, sessions, logging, url_for, redirect, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from flask_login import UserMixin,LoginManager, login_user, login_required, logout_user, current_user
import pandas as pd
import json
from livereload import Server


#flask intilisation
app = Flask(__name__)
app.config['SECRET_KEY'] = 'project'

#sqalchemy initilisation
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']= False #removes warning message
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
db = SQLAlchemy(app)

#flask_login initilisation
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

#used to create user table in sqlite3
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(200))
    email = db.Column(db.String(200), unique = True)
    password = db.Column(db.String(200))
    stock_list = db.relationship('Watchlist')

class Watchlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.Integer, unique = True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


@app.errorhandler(404)
def invalid_route(e):
    return render_template("error404.html")

#login
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                login_user(user, remember=True)#remmebers the user is logged in until they clear there browsing histroy
                return redirect(url_for('dashboard'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist.', category='error')

    return render_template("login.html")

#signup
@app.route("/signup", methods = ["GET","POST"])
def signup():
    if request.method =="POST":
        email = request.form.get('email')
        firstname = request.form.get('firstname')
        password = request.form.get('password')
        password1 = request.form.get('password1')

        user = User.query.filter_by(email=email).first()
        if user:
            flash("Email already exists.", category = 'error')#flash is a fetaure that is provided by flask which flashes a message. the category variable connects to sign_up.html
        elif len(email) < 4:
            flash("Email must be greater than 3 characters.", category = 'error')
        elif len(firstname) < 2:
            flash("First name must be greater than 1 character.", category = 'error')
        elif password != password1:
            flash("Passwords don\'t match.", category = 'error')
        elif len(password1) < 7:
            flash("Password must be at least 7 characters.", category = 'error')
        else:
            new_user = User(email=email, firstname=firstname, password=generate_password_hash(
            password, method='sha256'))
            db.session.add(new_user)
            db.session.commit()
            login_user(user)#remmebers the user is logged in until they clear there browsing histroy

            flash("Account created, you may now login",category = 'success')
            

    return render_template("sign_up.html")


@app.route("/signout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))



@app.route('/dashboard')
@login_required
def dashboard():
    connection = sqlite3.connect("app.db")
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cursor.execute(
        """
            SELECT id, symbol, name FROM stock ORDER BY symbol
    """
        )
    rows = cursor.fetchall()
    

    #get overall average sentiment
    avg = """SELECT ROUND(AVG(Polarity),3) as average_sentiment FROM (SELECT DISTINCT  Text, Polarity From tweets WHERE strftime('%Y-%m-%d', datetime(Timestamp, 'localtime')) = strftime('%Y-%m-%d',datetime('now', 'localtime')));"""
    #get number of negative tweets overall
    neg = """ SELECT COUNT(DISTINCT Text) FROM tweets WHERE Sentiment = "Negative" AND strftime('%Y-%m-%d', datetime(Timestamp, 'localtime')) = strftime('%Y-%m-%d',datetime('now', 'localtime'));"""
    #get number of positive tweets overall
    pos = """SELECT COUNT(DISTINCT Text) FROM tweets WHERE Sentiment = "Positive" AND strftime('%Y-%m-%d', datetime(Timestamp, 'localtime')) = strftime('%Y-%m-%d',datetime('now', 'localtime'));"""
    #get number of neutral tweets overall
    neu = """ SELECT COUNT(DISTINCT Text) FROM tweets WHERE Sentiment = "Neutral" AND strftime('%Y-%m-%d', datetime(Timestamp, 'localtime')) = strftime('%Y-%m-%d',datetime('now', 'localtime')); """
    #gets the stock that has most mentions
    most = """SELECT ticker from tweets WHERE (strftime('%Y-%m-%d', datetime(Timestamp, 'localtime')) = strftime('%Y-%m-%d',datetime('now', 'localtime'))) group by ticker ORDER BY count(ticker) DESC LIMIT 1;"""
    #gets the stock that has least mentions
    least = """ SELECT ticker from tweets WHERE (strftime('%Y-%m-%d', datetime(Timestamp, 'localtime')) = strftime('%Y-%m-%d',datetime('now', 'localtime')))group by ticker ORDER BY count(ticker) ASC LIMIT 1;"""
    #gets stock with highest average sentiment given that the stock has over 100 mentions
    most_avg = """SELECT ticker FROM tweets WHERE (strftime('%Y-%m-%d', datetime(Timestamp, 'localtime')) = strftime('%Y-%m-%d',datetime('now', 'localtime'))) Group by ticker HAVING count(ticker) >100 ORDER BY  ROUND(AVG(Polarity),3) DESC LIMIT 1 """
    #gets stock with lowest average sentiment given that the stock has over 100 mentions
    least_avg = """ SELECT ticker FROM tweets WHERE (strftime('%Y-%m-%d', datetime(Timestamp, 'localtime')) = strftime('%Y-%m-%d',datetime('now', 'localtime'))) Group by ticker HAVING count(ticker) >100 ORDER BY  ROUND(AVG(Polarity),3) ASC LIMIT 1"""

    df=pd.read_sql(avg, sqlite3.connect("app.db"))
    average = df.iat[0,0]
    df1 = pd.read_sql(neg, sqlite3.connect("app.db"))
    negative = df1.iat[0,0]
    df2 = pd.read_sql(pos,sqlite3.connect("app.db"))
    positive = df2.iat[0,0]
    df3 = pd.read_sql(neu,sqlite3.connect("app.db"))
    neutral = df3.iat[0,0]
    df4=pd.read_sql(most, sqlite3.connect("app.db"))
    if  df4.empty:
        most_symbol = '-'
    else:
        most_symbol = df4.iat[0,0]
   
    df5=pd.read_sql(least, sqlite3.connect("app.db"))
    if  df5.empty:
        least_symbol = '-'
    else:
        least_symbol = df5.iat[0,0]

    df6=pd.read_sql(most_avg, sqlite3.connect("app.db"))
    if  df6.empty:
        most_symbol_avg = '-'
    else:
        most_symbol_avg = df6.iat[0,0]
 
    df7=pd.read_sql(least_avg, sqlite3.connect("app.db"))
    if  df7.empty:
        least_symbol_avg = '-'
    else:
        least_symbol_avg = df7.iat[0,0]
  
    #converts the total number of neagtive, positive and neutral tweets into percentages 
    overall_negative = ((negative)/(negative+positive+neutral)) * 100 
    overall_positive = ((positive)/(negative+positive+neutral)) * 100 
    overall_neutral = ((neutral)/(negative+positive+neutral)) * 100 


    data = [
            ("Negative", overall_negative),
            ("Positive", overall_positive),
            ("Neutral", overall_neutral)
    ]
    labels = [row[0] for row in data]
    values = [row[1] for row in data]

    return render_template("dashboard.html", stocks=rows, values = values, labels = labels, average=average, positive=positive, negative = negative, neutral = neutral, most_symbol=most_symbol,
                            least_symbol=least_symbol, most_symbol_avg=most_symbol_avg, least_symbol_avg=least_symbol_avg )

@app.route("/tweets")
@login_required
def tweet():
    connection = sqlite3.connect("app.db")
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    #shows tweets streamed on the day i.e. if the date is 15/04/22, it will only show tweets that were gathered on the 15/04/22
    cursor.execute(
            """
        SELECT DISTINCT datetime(Timestamp, 'localtime') as Times , Text, Polarity, Sentiment FROM tweets WHERE strftime('%Y-%m-%d', Times) = strftime('%Y-%m-%d',datetime('now', 'localtime'))  ORDER BY Timestamp DESC
    """
        )
    rows = cursor.fetchall()
    connection.commit()
    return render_template("tweets.html", tweets=rows)


@app.route("/dashboard/<symbol>")
@login_required
def stockinfo(symbol):
    connection = sqlite3.connect("app.db")
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    try:
        cursor.execute(
            """
            SELECT id, symbol, name FROM stock where symbol =?
        """,
            (symbol,)
        )

        row = cursor.fetchone()
        #time is betwen 13:30 and 20:00 because date in the 'date' coloum is stored in UTC time zone. 'datetime(date,'localtime') as dates' changes it to localtime on users machine
        cursor.execute(
            """
            SELECT datetime(date,'localtime') as dates, open, high, low, close, volume FROM stock_price WHERE stock_id = ? AND (strftime('%H:%M:%S',date) BETWEEN '13:30:00' AND '20:00:00') ORDER by dates DESC
        """,
            (row["id"],),
        )
        prices = cursor.fetchall()
    #groups tweets into 5 minute increments e.g. if a tweet is was collected at 14:26, it will be rounded up to the closest 5 minute interval which in this case would be 14:30
        cursor.execute("""
            SELECT datetime(round(0.5+julianday((datetime(Timestamp, 'localtime')))*24*12)/24/12) AS times, count(Text) as s, ROUND(AVG(Polarity),3) as p FROM tweets WHERE ticker = ?
            AND ((datetime(Timestamp, 'localtime')) BETWEEN datetime('now','-1 day') AND datetime('now','localtime')) 
            AND (strftime('%H:%M:%S',times) BETWEEN '14:30:00' AND '21:00:00') GROUP BY times ORDER BY times DESC

                """, (row["symbol"],))
        compare = cursor.fetchall()
        #similar thing as in dashboard but this is for individual symbols
        avg = """ SELECT ROUND(AVG(Polarity),3) FROM tweets WHERE ticker = ? AND (strftime('%Y-%m-%d', datetime(Timestamp, 'localtime')) = strftime('%Y-%m-%d',datetime('now', 'localtime')))""" 
        neg = """ SELECT COUNT(DISTINCT Text) FROM tweets WHERE Sentiment = "Negative" AND ticker = ? AND (strftime('%Y-%m-%d', datetime(Timestamp, 'localtime')) = strftime('%Y-%m-%d',datetime('now', 'localtime')))"""
        pos = """ SELECT COUNT(DISTINCT Text) FROM tweets WHERE Sentiment = "Positive" AND ticker = ? AND (strftime('%Y-%m-%d', datetime(Timestamp, 'localtime')) = strftime('%Y-%m-%d',datetime('now', 'localtime')))"""
        neu = """ SELECT COUNT(DISTINCT Text) FROM tweets WHERE Sentiment = "Neutral" AND ticker = ? AND (strftime('%Y-%m-%d', datetime(Timestamp, 'localtime')) = strftime('%Y-%m-%d',datetime('now', 'localtime')))"""

        df = pd.read_sql(avg, sqlite3.connect("app.db"), params= (row["symbol"],))
        average = df.iat[0,0]
        df1 = pd.read_sql(neg, sqlite3.connect("app.db"), params= (row["symbol"],))
        negative = df1.iat[0,0]
        df2 = pd.read_sql(pos, sqlite3.connect("app.db"), params= (row["symbol"],))
        positive = df2.iat[0,0]
        df3 = pd.read_sql(neu, sqlite3.connect("app.db"), params= (row["symbol"],))
        neutral = df3.iat[0,0]

        negative_per = ((negative)/(negative+positive+neutral)) * 100 
        positive_per = ((positive)/(negative+positive+neutral)) * 100 
        neutral_per = ((neutral)/(negative+positive+neutral)) * 100 


        data = [
                ("Negative", negative_per),
                ("Positive", positive_per),
                ("Neutral", neutral_per)
        ]
        labels = [row[0] for row in data]
        values = [row[1] for row in data]
        

        connection.commit()
        return render_template("stockinfo.html", stock=row, bars=prices, symbol=symbol,labels = labels, values=values, average = average, positive = positive, negative = negative, neutral= neutral, compare = compare)

    except TypeError:
        print('symbol entered does not exist')
    
    return render_template("error404.html")
    

    
@app.route("/dashboard/<symbol>/dashboard/")
@login_required
def comparestock(symbol):
    connection = sqlite3.connect("app.db")
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    #symbol is the same symbol that was chosen by the user on the dashboard page
    cursor.execute(
        """
        SELECT id, symbol, name FROM stock where symbol =?
    """,
        (symbol,)
    )

    row = cursor.fetchone()
    #user can select a symbol that they want to compare to
    cursor.execute(
        """
            SELECT id, symbol, name FROM stock ORDER BY symbol
    """
        )
    row2 = cursor.fetchall()


    return render_template("compare_with.html", stock = row ,stock2=row2)


@app.route("/dashboard/<symbol>/dashboard/<symbol1>")
@login_required
def compare(symbol,symbol1):
    connection = sqlite3.connect("app.db")
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
   
    cursor.execute(
            """
            SELECT id, symbol, name FROM stock where symbol =?
        """,
            (symbol,)
        )
    row = cursor.fetchone()
    cursor.execute(
            """
            SELECT id, symbol, name FROM stock where symbol =?
        """,
            (symbol1,)
        )
    row2 = cursor.fetchone()

        #same querys that were used in stockinfo but have different variables. 
    avg = """ SELECT ROUND(AVG(Polarity),3) FROM tweets WHERE ticker = ? AND (strftime('%Y-%m-%d', datetime(Timestamp, 'localtime')) = strftime('%Y-%m-%d',datetime('now', 'localtime')))""" 
    neg = """ SELECT COUNT(DISTINCT Text) FROM tweets WHERE Sentiment = "Negative" AND ticker = ? AND (strftime('%Y-%m-%d', datetime(Timestamp, 'localtime')) = strftime('%Y-%m-%d',datetime('now', 'localtime')))"""
    pos = """ SELECT COUNT(DISTINCT Text) FROM tweets WHERE Sentiment = "Positive" AND ticker = ? AND (strftime('%Y-%m-%d', datetime(Timestamp, 'localtime')) = strftime('%Y-%m-%d',datetime('now', 'localtime')))"""
    neu = """ SELECT COUNT(DISTINCT Text) FROM tweets WHERE Sentiment = "Neutral" AND ticker = ? AND (strftime('%Y-%m-%d', datetime(Timestamp, 'localtime')) = strftime('%Y-%m-%d',datetime('now', 'localtime')))"""

    df = pd.read_sql(avg, sqlite3.connect("app.db"), params= (symbol,))
    average = df.iat[0,0]
    df1 = pd.read_sql(neg, sqlite3.connect("app.db"), params= (symbol,))
    negative = df1.iat[0,0]
    df2 = pd.read_sql(pos, sqlite3.connect("app.db"), params= (symbol,))
    positive = df2.iat[0,0]
    df3 = pd.read_sql(neu, sqlite3.connect("app.db"), params= (symbol,))
    neutral = df3.iat[0,0]

    negative_per = ((negative)/(negative+positive+neutral)) * 100 
    positive_per = ((positive)/(negative+positive+neutral)) * 100 
    neutral_per = ((neutral)/(negative+positive+neutral)) * 100 


    data = [
                ("Negative", negative_per),
                ("Positive", positive_per),
                ("Neutral", neutral_per)
        ]
    labels = [row[0] for row in data]
    values = [row[1] for row in data]
    
    
    avg1 = """ SELECT ROUND(AVG(Polarity),3) FROM tweets WHERE ticker = ? AND (strftime('%Y-%m-%d', datetime(Timestamp, 'localtime')) =strftime('%Y-%m-%d',datetime('now', 'localtime')))""" 
    neg1 = """ SELECT COUNT(DISTINCT Text) FROM tweets WHERE Sentiment = "Negative" AND ticker = ? AND (strftime('%Y-%m-%d', datetime(Timestamp, 'localtime')) = strftime('%Y-%m-%d',datetime('now', 'localtime')))"""
    pos1 = """ SELECT COUNT(DISTINCT Text) FROM tweets WHERE Sentiment = "Positive" AND ticker = ? AND (strftime('%Y-%m-%d', datetime(Timestamp, 'localtime')) = strftime('%Y-%m-%d',datetime('now', 'localtime')))"""
    neu1 = """ SELECT COUNT(DISTINCT Text) FROM tweets WHERE Sentiment = "Neutral" AND ticker = ? AND (strftime('%Y-%m-%d', datetime(Timestamp, 'localtime')) = strftime('%Y-%m-%d',datetime('now', 'localtime')))"""

    df4 = pd.read_sql(avg1, sqlite3.connect("app.db"), params= (symbol1,))
    average1 = df4.iat[0,0]
    df5 = pd.read_sql(neg1, sqlite3.connect("app.db"), params= (symbol1,))
    negative1 = df5.iat[0,0]
    df6 = pd.read_sql(pos1, sqlite3.connect("app.db"), params= (symbol1,))
    positive1 = df6.iat[0,0]
    df7 = pd.read_sql(neu1, sqlite3.connect("app.db"), params= (symbol1,))
    neutral1 = df7.iat[0,0]

    negative_per1 = ((negative1)/(negative1+positive1+neutral1)) * 100 
    positive_per1 = ((positive1)/(negative1+positive1+neutral1)) * 100 
    neutral_per1 = ((neutral1)/(negative1+positive1+neutral1)) * 100 


    datas = [
                ("Negative", negative_per1),
                ("Positive", positive_per1),
                ("Neutral", neutral_per1)
        ]
    labels1 = [row[0] for row in datas]
    values1 = [row[1] for row in datas]
    connection.commit()


    return render_template("compare.html", stock= row, stock2=row2 ,labels = labels, values= values,average = average, positive = positive, negative = negative, neutral= neutral, 
        average1 = average1, positive1 = positive1, negative1 = negative1, neutral1= neutral1, labels1 = labels1, values1=values1 )


@app.route('/watchlist', methods=['GET', 'POST'])
@login_required
def watchlist():
    connection = sqlite3.connect("app.db")
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    #list of symbols to create the drop down list
    cursor.execute(
        """
            SELECT  symbol FROM stock ORDER BY symbol
    """
        )
    rows = cursor.fetchall()
    #post request 
    if request.method == 'POST':
        request_stock=request.form.get('request_stock')
        new_stock = Watchlist(symbol = request_stock, user_id = current_user.id)
        db.session.add(new_stock)#adds this data into watchlist table using sqlalchemy
        db.session.commit()
    
    cursor.execute(""" SELECT DISTINCT symbol,id from Watchlist where user_id = ? GROUP by symbol""",
                    (current_user.id,))
    symbols  = cursor.fetchall()

    return render_template("watchlist.html", rows = rows,  symbols=symbols)

@app.route('/removefromwatchlist', methods=['POST'])
@login_required
def remove():
    #remove stock symbol from stock list, done using sqlalchemy
    watchlist = json.loads(request.data)
    watchlistId = watchlist['watchlistId']
    watchlist =  Watchlist.query.get(watchlistId)
    if watchlist:
        if watchlist.user_id == current_user.id:
            db.session.delete(watchlist)
            db.session.commit()
    return jsonify({})


if __name__ == '__main__':
    app.run(debug=True)
