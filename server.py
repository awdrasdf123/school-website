import os
import psycopg2
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = 'my-secret-key-2026'

# ============================================
# الاتصال بقاعدة البيانات (PostgreSQL)
# ============================================
def get_db():
    conn = psycopg2.connect(
        host=os.environ.get('DB_HOST'),
        database=os.environ.get('DB_NAME'),
        user=os.environ.get('DB_USER'),
        password=os.environ.get('DB_PASSWORD'),
        port=os.environ.get('DB_PORT')
    )
    return conn

# ============================================
# إنشاء الجدول (مرة واحدة)
# ============================================
def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id SERIAL PRIMARY KEY,
            name TEXT,
            email TEXT,
            message TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    cur.close()
    conn.close()

init_db()

# ============================================
# المسارات (Routes)
# ============================================
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    name = request.form['name']
    email = request.form['email']
    message = request.form['message']

    conn = get_db()
    cur = conn.cursor()
    cur.execute("INSERT INTO messages (name, email, message) VALUES (%s, %s, %s)", (name, email, message))
    conn.commit()
    cur.close()
    conn.close()

    flash("✅ تم إرسال رسالتك بنجاح!", "success")
    return redirect(url_for('home'))

@app.route('/messages')
def messages():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id, name, email, message, created_at FROM messages ORDER BY created_at DESC")
    all_messages = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('messages.html', messages=all_messages)

# ============================================
# تشغيل الخادم
# ============================================
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
