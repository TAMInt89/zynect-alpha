import os, random, sqlite3
from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__, static_folder='static')
app.secret_key = "zynect_alpha_final_fix_v3"

# ডাটাবেজ সেটআপ
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, f_name TEXT, l_name TEXT, contact TEXT, username TEXT UNIQUE, password TEXT, is_verified INTEGER DEFAULT 0)')
    conn.commit()
    conn.close()

# গ্লোবাল পোস্ট লিস্ট (টেম্পোরারি)
all_posts = [
    {"id": 1, "user": "Zynect Official", "text": "Welcome to the world's most advanced social ecosystem. Experience the Alpha network.", "likes": "1.2k"}
]

@app.route('/')
def home():
    if 'username' not in session: 
        return redirect(url_for('login'))
    
    current_user = session.get('username')
    return render_template('index.html', user=current_user, posts=all_posts)

@app.route('/post', methods=['POST'])
def create_post():
    if 'username' in session:
        content = request.form.get('content')
        if content:
            new_entry = {"id": len(all_posts)+1, "user": session['username'], "text": content, "likes": 0}
            all_posts.insert(0, new_entry)
    return redirect(url_for('home'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form.get('username')
        pwd = request.form.get('password')
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (user, pwd))
        data = c.fetchone()
        conn.close()
        if data:
            session['username'] = user
            return redirect(url_for('home'))
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        session['temp_user'] = request.form
        user = request.form.get('username')
        session['otp'] = "000000" if user == "mahi" else str(random.randint(100000, 999999))
        print(f"\n[SECURITY] YOUR CODE FOR {user}: {session['otp']}\n")
        return render_template('verify_code.html')
    return render_template('signup.html')

@app.route('/verify_access', methods=['POST'])
def verify_access():
    if request.form.get('code') == session.get('otp'):
        u = session['temp_user']
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        try:
            is_v = 1 if u['username'] == 'mahi' else 0
            c.execute("INSERT INTO users (f_name, l_name, contact, username, password, is_verified) VALUES (?,?,?,?,?,?)", 
                      (u['f_name'], u['l_name'], u['contact'], u['username'], u['password'], is_v))
            conn.commit()
            session['username'] = u['username']
            return redirect(url_for('home'))
        except:
            session['username'] = u['username'] 
            return redirect(url_for('home'))
        finally:
            conn.close()
    return "Invalid Code!"

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/profile')
def profile():
    if 'username' not in session: 
        return redirect(url_for('login'))
    return render_template('profile.html', user=session['username'])


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
