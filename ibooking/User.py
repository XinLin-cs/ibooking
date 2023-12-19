from flask import Flask, request, jsonify,session
from ibooking import api
from ibooking import app
from ibooking.models import db, User
from flask_restx import Resource, Namespace, fields
from sqlalchemy import or_
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from datetime import datetime, timedelta

# 初始化命名空间
user = Namespace('user', description='账户管理')

# 将命名空间添加到API
api.add_namespace(user)

# POST方法示例接口
@user.route('/TestAdd')
class TestAdd(Resource):
    # 定义数据模型
    user_model = api.model('User', {
        'name': fields.String(default = 'null'),
        'email': fields.String(default = 'null'),
        'password': fields.String(default = 'null')
    })
    # 定义POST方法
    @api.expect(user_model, validate=True)  
    def post(self):
        user = api.payload
        new_user = User(name=user['name'], email=user['email'], password=user['password'])
        db.session.add(new_user)
        db.session.commit()
        return {'message': 'User created successfully'}

@user.route('/Reset_db')
class Reset_db(Resource):
    def get(self):
        db.drop_all()
        db.create_all()
        users = User.query.all()
        return jsonify({'users': [user.to_dict() for user in users]})

# 注册接口
@user.route('/register')
class register(Resource):
    # 定义数据模型
    user_model = api.model('User1', {
        'name': fields.String(default = 'null'),
        'email': fields.String(default = 'null'),
        'password': fields.String(default = 'null'),
        'username': fields.String(default = 'null')
    })
    @api.expect(user_model, validate=True)      
    def post(self):
        data = request.get_json()
        name = data.get('name')
        email = data.get('email')
        password = data.get('password')
        username = data.get('username')

        # 判断用户名或邮箱是否已经被注册
        user = User.query.filter(or_(User.username == username, User.email == email)).first()
        if user:
            return jsonify({'status': 500, 'message': '用户名或邮箱已被注册，请重新输入','data':""})

        # 创建用户并保存到数据库
        hashed_password = generate_password_hash(password, method='sha256')
        user = User(name=name, email=email, password=hashed_password, username=username)
        db.session.add(user)
        db.session.commit()

        return jsonify({'status': 200, 'message': "注册成功",'data':user.id})


# 登录接口
@user.route('/login')
class login(Resource):
    # 定义数据模型
    user_model = api.model('User2', {
        'password': fields.String(default = 'null'),
        'username': fields.String(default = 'null')
    })
    @api.expect(user_model, validate=True)
    def post(self):
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        # 根据用户名或邮箱查找用户
        user = User.query.filter(or_(User.username == username)).first()

        # 判断用户是否存在
        if not user:
            return jsonify({'status': 500,'message': '该用户不存在，请检查输入','data':""})

        # 验证密码是否正确
        if not check_password_hash(user.password, password):
            return jsonify({'status': 500,'message': '密码错误，请重新输入','data':""})

        # 登录成功，返回用户信息和token
        
        session['userid'] = user.id

        return jsonify({'status': 200, 'message': "登录成功",'data':user.id})

# 登出接口
@user.route('/logout')
class logout(Resource):
    user_model = api.model('User3', {})    
    @api.expect(user_model, validate=True)
    def post(self):

        # userid置空
        session.pop('userid')

        return jsonify({'status': 200, 'message': '成功登出','data':[]})


# 注销接口
# @user.route('/logout')
# class logout(Resource):
#     user_model = api.model('User', {
#         'name': fields.String(default = 'null'),
#         'email': fields.String(default = 'null'),
#         'password': fields.String(default = 'null'),
#         'username': fields.String(default = 'null')
#     })    
#     @api.expect(user_model, validate=True)
#     def post(self):
#         data = request.get_json()
#         email = data.get('email')
#         password = data.get('password')

#         # 根据邮箱查找用户
#         user = User.query.filter_by(email=email).first()

#         # 判断用户是否存在
#         if not user:
#             return jsonify({'message': '该用户不存在，请检查输入'})

#         # 验证密码是否正确
#         if not check_password_hash(user.password, password):
#             return jsonify({'message': '密码错误，请重新输入'})

#         # 删除用户并提交到数据库
#         db.session.delete(user)
#         db.session.commit()

#         return jsonify({'message': '账户已成功注销'})