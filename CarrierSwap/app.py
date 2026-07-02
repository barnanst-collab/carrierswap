# (previous code + new routes)
@app.route('/listing/<int:listing_id>')
def listing_detail(listing_id):
    conn = get_db()
    listing = conn.execute('SELECT * FROM listings WHERE id = ?', (listing_id,)).fetchone()
    conn.close()
    return render_template('listing_detail.html', listing=listing)

@app.route('/express-interest/<int:listing_id>', methods=['POST'])
def express_interest(listing_id):
    flash('Interest expressed! (Chat would open in full version)')
    return redirect(url_for('listing_detail', listing_id=listing_id))

# Add to the end before if __name__
@app.route('/chat/<int:listing_id>')
def chat(listing_id):
    return render_template('chat.html', listing_id=listing_id)
