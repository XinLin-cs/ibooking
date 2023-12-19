
"""
The flask application package.
"""
from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from flask_restx import Api
from flask_mail import Mail
from flask_cors import CORS
from ibooking.funcs import getFile
import datetime

import os

settings = getFile('./settings.json')

# 创建flask实例
app = Flask(__name__)

# Flask-session配置
app.config['SECRET_KEY'] = os.urandom(24) # CSRF保护密钥
# app.config['WTF_CSRF_ENABLED'] = False # 关闭CSRF保护
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(days=7) # 设置session过期时间为一个月

# 数据库配置
app.config['SQLALCHEMY_DATABASE_URI'] = settings['db_connect']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # 关闭对模型修改的监控
db = SQLAlchemy(app)

# 邮件服务配置
app.config['MAIL_SERVER'] = 'smtp.126.com'
app.config['MAIL_PORT'] = 25
app.config['MAIL_USE_TLS'] = True
# app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = settings['mail']
app.config['MAIL_PASSWORD'] = settings['mail_key']
mail = Mail(app)

# 接口配置
api = Api(app)
import ibooking.User
import ibooking.Resource
import ibooking.Searching
import ibooking.Booking


# 定时脚本配置
from ibooking.Reminder import scheduler
scheduler.start()

# 设置跨域
CORS(app, supports_credentials=True)