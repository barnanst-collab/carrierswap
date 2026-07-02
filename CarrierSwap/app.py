from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from datetime import datetime

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
    c.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, email TEXT UNIQUE, display_name TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS listings (id INTEGER PRIMARY KEY, user_id INTEGER, current_station TEXT, current_city TEXT, desired TEXT, craft TEXT, experience INTEGER, notes TEXT)')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    conn = get_db()
    listings = conn.execute('SELECT * FROM listings ORDER BY id DESC').fetchall()
    conn.close()
    return render_template('index.html', listings=listings)

@app.route('/demo-login')
def demo_login():
    session['user_id'] = 1
    session['display_name'] = 'Demo Carrier'
    flash('Demo login successful!')
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    conn = get_db()
    my_listings = conn.execute('SELECT * FROM listings WHERE user_id = ?', (session['user_id'],)).fetchall()
    conn.close()
    return render_template('dashboard.html', my_listings=my_listings)

@app.route('/post', methods=['GET', 'POST'])
def post_listing():
    if request.method == 'POST':
        if 'user_id' not in session:
            return redirect(url_for('index'))
        conn = get_db()
        conn.execute('INSERT INTO listings (user_id, current_station, current_city, desired, craft, experience, notes) VALUES (?, ?, ?, ?, ?, ?, ?)',
                     (session['user_id'], request.form['current_station'], request.form.get('current_city', ''), request.form['desired'], request.form['craft'], request.form.get('experience', 5), request.form.get('notes', '')))
        conn.commit()
        conn.close()
        flash('Swap posted successfully!')
        return redirect(url_for('dashboard'))
    return render_template('post.html')

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
