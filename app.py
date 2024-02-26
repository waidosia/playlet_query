from hashlib import md5

from flask import Flask, request, jsonify, session, redirect, url_for
import psycopg2

app = Flask(__name__)
app.secret_key = "your_secret_key"  # 设置用于加密Session的密钥

# 连接到PG数据库
conn = psycopg2.connect(
    host="...",
    port="5432",
    database="",
    user="",
    password=""
)

# 创建用户表
def create_user_table():
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id SERIAL PRIMARY KEY,
            username VARCHAR(50) NOT NULL,
            password VARCHAR(50) NOT NULL,
            nickname VARCHAR(50)
        )
    """)
    conn.commit()


# 根据用户名查找用户
def find_user_by_username(username):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()
    return user

def encrypt_md5(s):
    # 创建md5对象
    new_md5 = md5()
    # 这里必须用encode()函数对字符串进行编码，不然会报 TypeError: Unicode-objects must be encoded before hashing
    new_md5.update(s.encode(encoding='utf-8'))
    # 加密
    return new_md5.hexdigest()


@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]
    password = encrypt_md5(password)
    user = find_user_by_username(username)
    if user and user[2] == password:
        session["username"] = username  # 将用户名保存到Session中
        return redirect(url_for("profile"))
    else:
        return "Invalid username or password", 401


@app.route("/profile")
def profile():
    if "username" in session:
        return f"Welcome, {session['username']}!"
    else:
        return "You are not logged in"


@app.route("/logout")
def logout():
    session.pop("username", None)  # 从Session中移除用户名
    return "Logged out successfully"


if __name__ == "__main__":
    # create_user_table()
    app.run()
