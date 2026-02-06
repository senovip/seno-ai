from flask import Flask, render_template, request, redirect, url_for
import os
import sqlite3

app = Flask(__name__)
DB_PATH = os.getenv("DATABASE_URL", "bot_database.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    conn = get_db_connection()
    users_count = conn.execute('SELECT count(*) FROM users').fetchone()[0]
    keys_count = conn.execute('SELECT count(*) FROM api_keys').fetchone()[0]
    conn.close()
    return f"""
    <html>
        <head>
            <title>لوحة تحكم بوت الذكاء الاصطناعي</title>
            <style>
                body {{ font-family: Arial; background: #121212; color: white; text-align: center; padding: 50px; }}
                .card {{ background: #1e1e1e; padding: 20px; border-radius: 10px; display: inline-block; margin: 10px; min-width: 200px; }}
                h1 {{ color: #00d1b2; }}
            </style>
        </head>
        <body>
            <h1>لوحة تحكم البوت المتقدمة 🚀</h1>
            <div class="card">
                <h2>المستخدمين</h2>
                <p>{users_count}</p>
            </div>
            <div class="card">
                <h2>مفاتيح API</h2>
                <p>{keys_count}</p>
            </div>
            <br><br>
            <p>المطور: <a href="https://t.me/idseno" style="color: #00d1b2;">@idseno</a></p>
        </body>
    </html>
    """

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv("PORT", 5000)))
