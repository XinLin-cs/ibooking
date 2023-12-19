from flask import Flask, request, jsonify
from ibooking import api
from ibooking import funcs
from ibooking.models import db, Booking, Room, Seat
from flask_restx import Resource, Namespace
from datetime import datetime

# 初始化命名空间
searching = Namespace('searching', description='搜索功能')

# 将命名空间添加到API
api.add_namespace(searching)

# 根据自习室id和时间段搜索座位
@searching.route('/Get')
class search_seats(Resource):
    def get(self):
        room_id = request.args.get("room_id")
        start_time = request.args.get("start_time")
        end_time = request.args.get("end_time")
        # 查询对应自习室的所有座位信息
        seats = Seat.query.filter_by(roomid=room_id).all()

        # 过滤出能够预约的座位信息
        available_seats = []
        for seat in seats:
            # 检查是否存在冲突的预定记录
            conflict_booking = Booking.query.filter_by(seatid=seat.id).filter(
                Booking.starttime < end_time, 
                Booking.finishtime > start_time,
                Booking.iscancel == 0, 
                Booking.isdefault == 0
            ).first()
            if not conflict_booking:
                available_seats.append({
                    'seatId': seat.id,
                    'roomId': seat.roomid,
                    'isCharge': seat.ischarge
                })

        # 返回结果
        return jsonify({
            'status': 200,
            'message': 'success',
            'data': available_seats
        })
