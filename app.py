import time
from hashlib import md5

from flask import Flask, request, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "playlet"  # 设置用于加密Session的密钥
app.permanent_session_lifetime = 60  # 设置Session的过期时间为60秒
app.config['PERMANENT_SESSION_LIFETIME'] = 60  # 设置Session的过期时间为60秒
app.config['SESSION_REFRESH_EACH_REQUEST'] = True  # 每个请求都刷新Session的过期时间

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://admin:CZ2000.07.16@175.178.123.76:5432/playlet'  # 替换为你的数据库连接信息
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)
    nickname = db.Column(db.String(50))

def encrypt_md5(s):
    # 创建md5对象
    new_md5 = md5()
    # 这里必须用encode()函数对字符串进行编码，不然会报 TypeError: Unicode-objects must be encoded before hashing
    new_md5.update(s.encode(encoding='utf-8'))
    # 加密
    return new_md5.hexdigest()


@app.before_request
def before_request():
    if 'last_activity' in session:
        last_activity = session['last_activity']
        current_time = time.time()
        if current_time - last_activity > 300:  # 如果用户最后活动时间超过300秒（5分钟），则注销用户
            session.pop('username', None)
    session['last_activity'] = time.time()  # 更新用户的最后活动时间


@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]
    password = encrypt_md5(password)
    user = User.query.filter_by(username=username).first()
    if user and user.password == password:
        session["username"] = username  # 将用户名保存到Session中
        session.permanent = True  # 设置Session为永久有效
        return redirect(url_for("profile"))
    else:
        return "Invalid username or password", 401


@app.route("/profile")
def profile():
    if "username" in session:
        session.modified = True  # 标记Session已被修改
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
