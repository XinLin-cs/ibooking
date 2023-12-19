from flask import Flask, request, jsonify, session
from ibooking import api
from ibooking import funcs
from ibooking.models import db, Room, User, Seat, Booking
from flask_restx import Resource, Namespace, fields
from datetime import datetime, timedelta
from sqlalchemy import and_, or_

# 初始化命名空间
booking = Namespace('booking', description='预定功能')

# 将命名空间添加到API
api.add_namespace(booking)


# 预定座位
@booking.route('/create')
class create(Resource):
    # 定义数据模型
    create_model = api.model('bookingReq', {
        'seat_id': fields.String(default='1'),
        'start_time': fields.String(default='2023-05-26 17:00:00'),
        'end_time': fields.String(default='2023-05-26 18:00:00')
    })
    # 定义POST方法
    @api.expect(create_model, validate=True)  
    def post(self):
        seat_id = api.payload['seat_id']
        start_time = api.payload['start_time']
        end_time = api.payload['end_time']
        #获取用户id
        user_id = session.get('userid')
        if not user_id:
            return jsonify({
                'status':532,
                'message':'用户未登录',
                'data':[]
            })
        if not seat_id or not user_id or not start_time or not end_time:
            return jsonify({
                'status':533,
                'message':'预定信息缺失',
                'data':[]
            })

        seat = Seat.query.filter(Seat.id==seat_id).all()
        if not seat:
            return jsonify({
                'status':534,
                'message':'座位不存在',
                'data':[]
            })
            
        # 检查座位在指定时间段内是否已被预定
        existing_bookings = Booking.query.filter(
            Booking.seatid == seat_id,
            Booking.isdefault != '1',
            Booking.iscancel != '1',
            or_(
                and_(Booking.starttime < start_time, Booking.finishtime > start_time),
                and_(Booking.starttime < end_time, Booking.finishtime > end_time),
                and_(Booking.starttime >= start_time, Booking.finishtime <= end_time),
            )
        ).all()

        if existing_bookings:
            return jsonify({
                'status':535,
                'message':'该时段座位已被预定',
                'data':[]
            })
        
        # 创建新的预定记录
        booking = Booking(
            seatid=seat_id,
            userid=user_id,
            starttime=start_time,
            finishtime=end_time,
            booktime=datetime.now(),
            isdefault='0',
            iscancel='0',
            ischeckin='0',
        )
        db.session.add(booking)
        db.session.commit()

        return jsonify({
            'status':200,
            'message':'预定成功',
            'data':booking.id
        })


# 查询预定记录
@booking.route('/get_bookings')
class get_bookings(Resource):
    def get(self):
        #获取用户id
        user_id = session.get('userid')
        if not user_id:
            return jsonify({
                'status':532,
                'message':'用户未登录',
                'data':[]
            })
        # 查询用户的所有预定记录
        bookings = Booking.query.filter_by(userid=user_id).all()
        # 构造返回结果
        result = []
        for booking in bookings:
            result.append({
                'bid': booking.id,
                'seat_id': booking.seatid,
                'booktime': booking.booktime,
                'start_time': booking.starttime,
                'end_time': booking.finishtime
            })
        return jsonify({
            'status':200,
            'message':'预定记录',
            'data':result
        })

# 用户签到
@booking.route('/checkin')
class checkin(Resource):
    # 定义数据模型
    checkin_model = api.model('checkin', {
        'booking_id': fields.String(default='1')
    })
    # 定义Post方法
    @api.expect(checkin_model, validate=True)  
    def post(self):
        booking_id = api.payload['booking_id']

        # 查询预定记录
        booking = Booking.query.get(booking_id)

        if not booking:
            return jsonify({
                'status':536,
                'message': '座位号无效，无法签到',
                'data':[]
            })

        # 检查预定记录的状态
        if booking.isdefault == '1':
            return jsonify({
                'status':537,
                'message': '此预定已违约，无法签到',
                'data':[]
            })

        if booking.iscancel == '1':
            return jsonify({
                'status':538,
                'message': '此预定已取消，无法签到',
                'data':[]
            })
        
        # 计算签到时间是否在预定时间的前后十五分钟
        now = datetime.now()
        start_time = datetime.strptime(booking.starttime, '%Y-%m-%d %H:%M:%S')
        time_diff = (now - start_time).total_seconds() / 60

        if time_diff < -30 or time_diff > 15:
            return jsonify({
                'status':536,
                'message': '不在签到时间范围内',
                'data':[]
            })

        # 更新预定记录的签到状态
        booking.ischeckin = '1'
        db.session.commit()

        return jsonify({
            'status':200,
            'message': '成功签到',
            'data':[]
        })

# 取消预定
@booking.route('/cancel')
class cancel(Resource):
    # 定义数据模型
    canceling_model = api.model('cancel', {
        'booking_id': fields.String(default='1')
    })
    # 定义Post方法
    @api.expect(canceling_model, validate=True)  
    def post(self):
        booking_id = api.payload['booking_id']
        booking = Booking.query.filter_by(id=booking_id).first()

        # 检查是否在取消时间范围内
        start_time = datetime.strptime(booking.starttime, '%Y-%m-%d %H:%M:%S')
        if datetime.now() > start_time:
            return jsonify({
                'status':535,
                'message':'已经过了取消预定的时间！',
                'data':[]
            })

        # 更新预定记录状态
        booking.iscancel = '1'
        db.session.commit()

        return jsonify({
            'status':200,
            'message':'预定已成功取消',
            'data':[]
        })
            

# 违约查询
@booking.route('/get_defaults')
class get_defaults(Resource):
    def get(self):
        #获取用户id
        user_id = session.get('userid')
        if not user_id:
            return jsonify({
                'status':532,
                'message':'用户未登录',
                'data':[]
            })
        # 查询用户的所有预定记录
        bookings = Booking.query.filter_by(userid=user_id).all()

        # 筛选出已经违约的预定记录
        default_bookings = [booking for booking in bookings if booking.isdefault=='1']

        # 构造响应数据
        data = []
        for booking in default_bookings:
            item = {
                'id': booking.id,
                'seatid': booking.seatid,
                'booktime': booking.booktime,
                'starttime': booking.starttime,
                'finishtime': booking.finishtime,
            }
            data.append(item)

        return jsonify({
            'status':200,
            'message':'违约记录',
            'data':data
        })

# 待完成预定查询
@booking.route('/get_current')
class get_defaults(Resource):
    def get(self):
        #获取用户id
        user_id = session.get('userid')
        if not user_id:
            return jsonify({
                'status':532,
                'message':'用户未登录',
                'data':[]
            })
        # 查询用户的所有预定记录
        bookings = Booking.query.filter_by(userid=user_id).all()

        # 筛选出待完成的预定记录
        default_bookings = [booking for booking in bookings if booking.isdefault=='0' and booking.iscancel=='0' and datetime.strptime(booking.finishtime, '%Y-%m-%d %H:%M:%S')>datetime.now()]

        # 构造响应数据
        data = []
        for booking in default_bookings:
            item = {
                'id': booking.id,
                'seatid': booking.seatid,
                'booktime': booking.booktime,
                'starttime': booking.starttime,
                'finishtime': booking.finishtime,
            }
            data.append(item)

        return jsonify({
            'status':200,
            'message':'待完成预定',
            'data':data
        })