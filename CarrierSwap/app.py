from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from datetime import datetime
from functools import wraps

app = Flask(__name__)
app.secret_key = 'carrierswap-secret'

DATABASE = 'carrierswap.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, email TEXT UNIQUE, display_name TEXT, station TEXT, craft TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS listings (id INTEGER PRIMARY KEY, user_id INTEGER, current_station TEXT, current_city TEXT, desired TEXT, craft TEXT, experience INTEGER, notes TEXT)''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/demo-login')
def demo_login():
    session['user_id'] = 1
    flash('Demo login successful!')
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/post', methods=['GET', 'POST'])
def post_listing():
    if request.method == 'POST':
        flash('Swap posted!')
        return redirect(url_for('dashboard'))
    return render_template('post.html')

if __name__ == '__main__':
    init_db()
    print("CarrierSwap is running!")
    app.run(debug=False, host='0.0.0.0', port=5000)
