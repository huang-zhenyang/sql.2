from flask import Flask, request, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
import os
from flask import session
from flask import jsonify
from flask_cors import CORS



app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mydatabase.db'
app.config['SECRET_KEY'] = os.urandom(24).hex()
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# 在应用的上下文中创建所有表
with app.app_context():
    db.create_all()

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    通关次数 = db.Column(db.Integer, default=0, nullable=False)
    game_history = db.Column(db.Text, default='[]')  # 存储游戏历史记录

    def __repr__(self):
        return '<User %r>' % self.username

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()  # 获取JSON数据
    username = data['username']
    password = data['password']
    user = User.query.filter_by(username=username).first()
    
    if user and check_password_hash(user.password_hash, password):
        session['username'] = user.username
        session['user_id'] = user.id
        return jsonify({'message': '您已成功登录'}), 200
    else:
        flash('用户名或密码错误。已自动为您创建新用户。')
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password_hash=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'message': '新用户创建成功'}), 201
    
    

@app.route('/dashboard')
def dashboard():
    username = session.get('username')  # 从session中获取用户名
    if not username:  # 如果session中没有用户名，可能用户未登录
        return redirect(url_for('login'))  # 重定向到登录页面
    user = User.query.filter_by(username=username).first()
    return render_template('App.html', title='寻宝游戏', user=user, 通关次数=user.通关次数)

@app.route('/complete_level', methods=['POST'])
def complete_level():
    username = session.get('username')
    if not username:
        return jsonify({'message': 'User not logged in'}), 401

    user = User.query.filter_by(username=username).first()
    if user:
        if user.通关次数 is None:
            user.通关次数 = 0
            user.通关次数 += 1
        
        db.session.commit()
        return jsonify({'message': 'Level completed successfully'}), 200
    else:
        return jsonify({'message': 'User not found'}), 404

@app.route('/')
def home():
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)