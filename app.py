from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'journey_secret_key'

def init_db():
    conn = sqlite3.connect('journey.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (id INTEGER PRIMARY KEY, username TEXT UNIQUE, total_found INTEGER DEFAULT 0)''')
    conn.commit()
    conn.close()

def get_milestones():
    return [
        {"name": "Little Pilgrim", "count": 5, "icon": "🥉"},
        {"name": "Seeker of Light", "count": 10, "icon": "🥈"},
        {"name": "Faithful Explorer", "count": 25, "icon": "🥇"},
        {"name": "Centurion Disciple", "count": 100, "icon": "🏆"}
    ]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    username = request.form['username'].strip()
    try:
        found_now = int(request.form['found_count'])
    except ValueError:
        found_now = 0
    
    # Check for photo submission bonus
    bonus_points = 0
    if 'photo' in request.files:
        photo = request.files['photo']
        # If a file was actually selected
        if photo.filename != '':
            bonus_points = 5 

    if not username or found_now <= 0:
        flash("Please enter a valid name and count.")
        return redirect(url_for('index'))

    conn = sqlite3.connect('journey.db')
    c = conn.cursor()
    
    # Calculate total: Number found + 5 point proof bonus
    points_to_add = found_now + bonus_points
    
    c.execute("SELECT total_found FROM users WHERE username=?", (username,))
    row = c.fetchone()
    
    if row:
        new_total = row[0] + points_to_add
        c.execute("UPDATE users SET total_found=? WHERE username=?", (new_total, username))
    else:
        new_total = points_to_add
        c.execute("INSERT INTO users (username, total_found) VALUES (?, ?)", (username, new_total))
    
    conn.commit()
    conn.close()
    
    # Feedback message
    msg = f"Found {found_now}!"
    if bonus_points > 0:
        msg += " +5 Bonus for the photo proof! 📸"
    flash(f"{msg} Total: {new_total}")
    
    return redirect(url_for('view_medals', username=username))

@app.route('/medals')
@app.route('/medals/<username>')
def view_medals(username=None):
    conn = sqlite3.connect('journey.db')
    c = conn.cursor()
    
    if username:
        c.execute("SELECT total_found FROM users WHERE username=?", (username,))
        row = c.fetchone()
        total = row[0] if row else 0
        conn.close()
        return render_template('medals.html', total=total, milestones=get_milestones(), username=username)
    else:
        c.execute("SELECT username, total_found FROM users ORDER BY total_found DESC LIMIT 10")
        top_travelers = c.fetchall()
        conn.close()
        return render_template('leaderboard.html', travelers=top_travelers)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)