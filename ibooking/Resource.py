from flask import Flask, request, jsonify
from ibooking import api
from ibooking import funcs
from ibooking.models import db, Room, Seat
from sqlalchemy import or_
from flask_restx import Resource, Namespace,fields


# 初始化命名空间
resource = Namespace('resource', description='资源管理')

# 将命名空间添加到API
api.add_namespace(resource)

# 获取自习室信息
@resource.route('/getroom')
class room_get(Resource):
    def get(self):
        rooms = Room.query.all()
        result = []
        for room in rooms:
            result.append({
                'id': room.id,
                'number': room.number,
                'latitude': room.latitude,
                'longitude': room.longitude,
                'maxvolume': room.maxvolume,
                'note': room.note
            })
        return jsonify({'status':200, 'message':'get room successfully', 'data': result})

# 创建自习室
@resource.route('/addroom')
class add_room(Resource):
    # 定义数据模型
    room_model = api.model('Room1', {
        'number': fields.String(default = '0'),
        'latitude': fields.Float(default = '0'),
        'longitude': fields.Float(default = '0'),
        'maxvolume':fields.Integer(default = '50'),
        'note':fields.String(default = '7:00-22:00')
    })
    @api.expect(room_model)
    def post(self):
        data = request.get_json()
        number = data['number']
        maxvolume = int(data['maxvolume'])
        latitude = float(data['latitude'])
        longitude = float(data['longitude'])
        note = data['note']
        room = Room(number=number, maxvolume=maxvolume, latitude=latitude, longitude=longitude, note = note)
        db.session.add(room)
        db.session.commit()
        for i in range(maxvolume):
            seat = Seat(roomid = number, number = i, ischarge = '0', isdisabled = '0')
            db.session.add(seat)
            db.session.commit()
        return jsonify({'status':200, 'message': 'Room added successfully!', 'data':''})

# 删除自习室
@resource.route('/deleteroom')
class delet_room(Resource):
    # 定义数据模型
    room_model = api.model('Room2', {
        'number': fields.String(default = '0')
    })    
    @api.expect(room_model)
    def post(self):
        data = request.get_json()
        number = data['number']

        # 根据编号查找自习室
        room = Room.query.filter_by(number=number).first()

        # 判断该自习室是否存在
        if not room:
            return jsonify({'status':500, 'message':'该自习室不存在，请检查输入', 'data':''})
        
        # 查询某一自习室的所有座位信息
        room_seats = Seat.query.filter_by(roomid=number).all()

        # 删除自习室并提交到数据库
        for seat in room_seats:
            db.session.delete(seat)
        db.session.delete(room)
        db.session.commit()
        return jsonify({'status':200, 'message': 'Room deleted successfully!', 'data':''})
    
# 修改自习室信息
@resource.route('/modifyroom')
class modify_room(Resource):
    # 定义数据模型
    room_model = api.model('Room3', {
        'id':fields.String(default = '0'),
        'number': fields.String(default = '0'),
        'latitude': fields.Float(default = '0'),
        'longitude': fields.Float(default = '0'),
        'maxvolume':fields.Integer(default = '50')
    })    
    @api.expect(room_model)
    def post(self):
        data = request.get_json()
        room_id = data['id']
        number = data['number']
        maxvolume = data['maxvolume']
        latitude = data['latitude']
        longitude = data['longitude']
        room = Room.query.filter_by(id=room_id).first()
        if not room:
            return jsonify({'status':500, 'message':'该自习室不存在，请检查输入', 'data':''})
        room.number = number
        room.maxvolume = maxvolume
        room.latitude = latitude
        room.longitude = longitude
        
        db.session.commit()
        return jsonify({'status':200, 'message': 'Room modify successfully!', 'data':''})
    
# 获取座位信息
@resource.route('/getseat')
class seat_get(Resource):
    def get(self):
        seats = Seat.query.all()
        return jsonify({'status':200, 'message':'get seat successfully', 'data': [seat.to_dict() for seat in seats]})

# 获取某一自习室中的座位信息
@resource.route('/get_room_seat/<string:room_id>')
class get_room_seat(Resource):
    def get(self, room_id):
        # 查询某一自习室的所有座位信息
        room_seats = Seat.query.filter_by(roomid=room_id).all()
        # 构造返回结果
        result = []
        for room_seat in room_seats:
            result.append({
                'seat_id': room_seat.id,
                'seat_number': room_seat.number,
                'seat_ischarge': room_seat.ischarge
            })
        return jsonify(result)

#添加座位
@resource.route('/addseat')
class add_seat(Resource):
    # 定义数据模型
    seat_model = api.model('Seat1', {
        'roomid': fields.String(default = 'null'),
        'number': fields.Float(default = '0'),
        'ischarge': fields.Float(default = '0'),
        'freetime':fields.Integer(default = '150000'),
        'usingtime':fields.Integer(default = '150000'),
        'bookedtime':fields.Integer(default = '150000')
    })    
    @api.expect(seat_model)
    def post(self):
        data = request.get_json()
        roomid = data['roomid']
        number = data['number']
        ischarge = data['ischarge']
        freetime = data['freetime']
        usingtime = data['usingtime']
        bookedtime = data['bookedtime']

        # 判断自习室是否存在
        isroom = Room.query.filter_by(roomid = roomid).first()
        if not isroom:
            return jsonify({'message':'不存在该自习室，请检查输入'})
        
        isseat = Seat.query.filter_by(number = number).first()
        if isseat:
            return jsonify({'message':'该座位已存在，请检查输入'})        

        seat = Seat(roomid = roomid, number=number, ischarge=ischarge, freetime=freetime, usingtime=usingtime, bookedtime = bookedtime)
        db.session.add(seat)
        db.session.commit()
        return jsonify({'message': 'Seat added successfully!'})

# 删除座位
@resource.route('/deleteseat')
class delet_seat(Resource):
    # 定义数据模型
    seat_model = api.model('Seat2', {
        'roomid': fields.String(default = 'null'),
        'number': fields.Float(default = '0'),
        'ischarge': fields.Float(default = '0'),
        'freetime':fields.Integer(default = '150000'),
        'usingtime':fields.Integer(default = '150000'),
        'bookedtime':fields.Integer(default = '150000')
    })   
    @api.expect(seat_model)
    def post(self):
        data = request.get_json()
        roomid = data['roomid']
        number = data['number']
        
        # 根据编号查找座位
        seat = Seat.query.filter(or_ (Seat.roomid == roomid, Seat.number == number)).first()
        # 判断该座位是否存在
        if not seat:
            return jsonify({'message':'输入有错误，请检查输入'})        
        
        # 删除自习室并提交到数据库
        db.session.delete(seat)
        db.session.commit()
        return jsonify({'message': 'seat deleted successfully!'})
    
# 修改座位信息
@resource.route('/modifyseat')
class modify_seat(Resource):
    # 定义数据模型
    seat_model = api.model('Seat3', {
        'id':fields.String(default = 'null'),
        'isdisabled':fields.String(default = '0'),
        'number': fields.String(default = '0'),
        'ischarge': fields.String(default = '0')
    })    
    @api.expect(seat_model)
    def post(self):
        data = request.get_json()
        id = data['id']
        number = data['number']
        ischarge = data['ischarge']
        isdisabled = data['isdisabled']
        # 根据编号查找座位
        seat = Seat.query.filter(Seat.id == id).first()
        # 判断该座位是否存在
        if not seat:
            return jsonify({'status':500, 'messagischargee':'输入有错误，请检查输入', 'data':''})      
        seat.number = number
        seat.ischarge = ischarge
        seat.isdisabled = isdisabled
        db.session.commit()
        return jsonify({'status':200, 'message': 'seat modify successfully!', 'data':''})

# 附近最近自习室
@resource.route('/sortedrooms')
class get_rooms(Resource):
    def get(self):
        latitude = request.args.get('latitude')
        longitude = request.args.get('longitude')
        rooms = Room.query.all()
        rooms_with_distance = []
        for room in rooms:
            distance = funcs.calculate_distance(latitude, longitude, room.latitude, room.longitude)
            rooms_with_distance.append({'id': room.id, 'number': room.number, 'distance': distance})
        sorted_rooms = sorted(rooms_with_distance, key=lambda x: x['distance'])
        return jsonify(sorted_rooms)