from flask import Flask, render_template, request, redirect, flash
from flask_mysqldb import MySQL
import requests

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# MySQL configurations
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '1234'
app.config['MYSQL_DB'] = 'website'
mysql = MySQL(app)

# API keys
STOCK_API_KEY = "U4JA4DW52WRXEA5Z"
NEWS_API_KEY = "2beef05de906477694e596bcf3d72110"


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)", (username, email, password))
        mysql.connection.commit()
        cur.close()

        flash('You have successfully signed up!')
        return redirect('/login')

    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email = %s AND password = %s", (email, password))
        user = cur.fetchone()
        cur.close()

        if user:
            # Store the user's session or set a cookie to maintain login state
            flash('You have successfully logged in!')
            return redirect('/dashboard')
        else:
            flash('Invalid email or password. Please try again.')
            return redirect('/login')

    return render_template('login.html')


@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    # Check if the user is logged in before accessing the dashboard
    # You can use session or cookie to maintain the login state

    if request.method == 'POST':
        company1 = request.form.get('company1')
        company2 = request.form.get('company2')
        company3 = request.form.get('company3')

        # Fetch stock data
        stock_data = fetch_stock_data([company1, company2, company3])
        # Fetch news data
        news_data = fetch_news_data(company1)

        return render_template('dashboard.html', stock_data=stock_data, news_data=news_data)

    return render_template('dashboard.html', stock_data=None, news_data=None)


def fetch_stock_data(companies):
    stock_data = []
    for company in companies:
        params = {
            "function": "TIME_SERIES_WEEKLY",
            "symbol": company,
            "apikey": STOCK_API_KEY
        }
        response = requests.get("https://www.alphavantage.co/query", params=params)

        try:
            data = response.json()
        except ValueError:
            # If response is not valid JSON, skip this company and continue to the next one
            continue

        if 'Weekly Time Series' in data:
            stock_data.append({
                'symbol': company,
                'data': data['Weekly Time Series']
            })
    return stock_data


def fetch_news_data(company):
    params = {
        "q": company,
        "apiKey": NEWS_API_KEY
    }
    response = requests.get("https://newsapi.org/v2/everything", params=params)
    data = response.json()
    return data


if __name__ == '__main__':
    app.run(debug=True)