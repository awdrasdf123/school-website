import os
import psycopg2
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify

app = Flask(__name__)
app.secret_key = 'my_super_secret_key_123'

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
# دوال مساعدة
# ============================================
def get_student_by_id(student_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT name, class, level, average, behavior, absences FROM students WHERE id = %s", (student_id,))
    student = cur.fetchone()
    cur.close()
    conn.close()
    if student:
        return {
            "name": student[0],
            "class": student[1],
            "level": student[2],
            "average": student[3],
            "behavior": student[4],
            "absences": student[5]
        }
    return None

# ============================================
# الصفحة الرئيسية
# ============================================
@app.route('/')
def home():
    return render_template('index.html')

# ============================================
# استقبال البيانات من نموذج الاتصال وحفظها
# ============================================
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

# ============================================
# عرض جميع الرسائل
# ============================================
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
# حذف رسالة
# ============================================
@app.route('/delete/<int:id>')
def delete_message(id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM messages WHERE id = %s", (id,))
    conn.commit()
    cur.close()
    conn.close()
    return "🗑️ تم حذف الرسالة! <a href='/messages'>العودة إلى القائمة</a>"

# ============================================
# صفحة تعديل رسالة (عرض النموذج)
# ============================================
@app.route('/edit/<int:id>')
def edit_message(id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id, name, email, message FROM messages WHERE id = %s", (id,))
    msg = cur.fetchone()
    cur.close()
    conn.close()
    return render_template('edit.html', msg=msg)

# ============================================
# تحديث رسالة (حفظ التعديلات)
# ============================================
@app.route('/update/<int:id>', methods=['POST'])
def update_message(id):
    name = request.form['name']
    email = request.form['email']
    message = request.form['message']

    conn = get_db()
    cur = conn.cursor()
    cur.execute("UPDATE messages SET name = %s, email = %s, message = %s WHERE id = %s", (name, email, message, id))
    conn.commit()
    cur.close()
    conn.close()

    return "✅ تم تعديل الرسالة! <a href='/messages'>العودة إلى القائمة</a>"

# ============================================
# شات بوت (قواعد بسيطة)
# ============================================
@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.form['message'].strip().lower()
    reply = "❓ لم أفهم سؤالك. يرجى التواصل مع إدارة المدرسة."

    if "رقم" in user_message or "هاتف" in user_message:
        reply = "📞 رقم مدرسة النور: 0123456789"
    elif "عنوان" in user_message or "موقع" in user_message:
        reply = "📍 عنوان المدرسة: شارع النور، المدينة التعليمية"
    elif "وقت" in user_message or "دوام" in user_message:
        reply = "⏰ أوقات العمل: من 8 صباحاً إلى 2 ظهراً (الأحد إلى الخميس)"
    elif "مرحب" in user_message or "السلام" in user_message:
        reply = "👋 أهلاً بك! كيف يمكنني مساعدتك؟"
    elif "شكر" in user_message:
        reply = "🙏 العفو! نحن في خدمتك دائماً."

    return reply

# ============================================
# API لتسجيل الدخول (لتطبيق الهاتف)
# ============================================
@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM parents WHERE username = %s AND password = %s", (username, password))
    parent = cur.fetchone()
    cur.close()
    conn.close()

    if parent:
        student = get_student_by_id(parent[3])  # student_id
        if student:
            return jsonify({"success": True, "student": student})
        else:
            return jsonify({"success": False, "message": "لا يوجد طالب مرتبط بهذا الحساب"}), 404
    else:
        return jsonify({"success": False, "message": "بيانات الدخول غير صحيحة"}), 401

# ============================================
# تشغيل الخادم
# ============================================
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
