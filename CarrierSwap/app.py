from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3

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
        flash('Swap posted!')
        return redirect(url_for('dashboard'))
    return render_template('post.html')

@app.route('/listing/<int:listing_id>')
def listing_detail(listing_id):
    conn = get_db()
    listing = conn.execute('SELECT * FROM listings WHERE id = ?', (listing_id,)).fetchone()
    conn.close()
    return render_template('listing_detail.html', listing=listing)

@app.route('/express-interest/<int:listing_id>', methods=['POST'])
def express_interest(listing_id):
    flash('Interest expressed!')
    return redirect(url_for('listing_detail', listing_id=listing_id))
    
@app.route('/express-interest/<int:listing_id>', methods=['POST'])
def express_interest(listing_id):
    if 'user_id' not in session:
        return redirect(url_for('index'))
    conn = get_db()
    conn.execute('INSERT OR IGNORE INTO interests (listing_id, interested_user_id) VALUES (?, ?)', (listing_id, session['user_id']))
    conn.commit()
    conn.close()
    flash('Interest expressed!')
    return redirect(url_for('listing_detail', listing_id=listing_id))
if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
