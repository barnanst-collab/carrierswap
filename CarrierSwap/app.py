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
    c.execute('CREATE TABLE IF NOT EXISTS interests (id INTEGER PRIMARY KEY, listing_id INTEGER, interested_user_id INTEGER)')
    c.execute('CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY, listing_id INTEGER, from_user_id INTEGER, to_user_id INTEGER, content TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)')
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
        flash('Swap posted!')
        return redirect(url_for('dashboard'))
    return render_template('post.html')

@app.route('/listing/<int:listing_id>')
def listing_detail(listing_id):
    conn = get_db()
    listing = conn.execute('SELECT * FROM listings WHERE id = ?', (listing_id,)).fetchone()
    conn.close()
    if not listing:
        flash('Listing not found.')
        return redirect(url_for('index'))
    return render_template('listing_detail.html', listing=listing)

@app.route('/express-interest/<int:listing_id>', methods=['POST'])
def express_interest(listing_id):
    if 'user_id' not in session:
        return redirect(url_for('index'))
    conn = get_db()
    conn.execute('INSERT OR IGNORE INTO interests (listing_id, interested_user_id) VALUES (?, ?)', (listing_id, session['user_id']))
    conn.commit()
    conn.close()
    flash('Interest expressed! Opening chat...')
    return redirect(url_for('chat', listing_id=listing_id))

@app.route('/chat/<int:listing_id>', methods=['GET', 'POST'])
def chat(listing_id):
    if 'user_id' not in session:
        return redirect(url_for('index'))
    conn = get_db()
    if request.method == 'POST':
        content = request.form['content']
        conn.execute('INSERT INTO messages (listing_id, from_user_id, to_user_id, content) VALUES (?, ?, ?, ?)', (listing_id, session['user_id'], 2, content))
        conn.commit()
    messages = conn.execute('SELECT * FROM messages WHERE listing_id = ? ORDER BY created_at', (listing_id,)).fetchall()
    conn.close()
    return render_template('chat.html', listing_id=listing_id, messages=messages)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        conn = get_db()
        user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        conn.close()
        if user:
            session['user_id'] = user['id']
            session['display_name'] = user['display_name']
            flash('Logged in!')
            return redirect(url_for('dashboard'))
        flash('User not found.')
    return render_template('login.html')

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
