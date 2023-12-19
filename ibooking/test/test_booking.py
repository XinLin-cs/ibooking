import pytest
from ibooking import app, db
from ibooking.models import Room, Seat, Booking, User
from datetime import datetime, timedelta
from flask import session
from copy import deepcopy
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import Session, sessionmaker

# 创建一个fixture，用于在每个测试用例执行前创建一个新的嵌套事务，并在测试完成后回滚该事务
@pytest.fixture(scope='module')
def test_session():
    with app.app_context():        
        connection = db.engine.connect()
        transaction = connection.begin()

        options = dict(bind=connection, binds={})
        session = db.scoped_session(db.sessionmaker(**options))

        db.session = session

        yield session

        transaction.rollback()
        connection.close()
        session.remove()

# 服务器静态数据
@pytest.fixture(scope='module')
def test_data(test_session):
    with app.app_context():        
        room = Room(number='test', latitude='30.1234', longitude='120.5678', maxvolume='50')
        test_session.add(room)
        test_session.commit()

        seat = Seat(number='test01', roomid=room.id)
        test_session.add(seat)
        test_session.commit()
        
        hashed_password = generate_password_hash('123456', method='sha256')
        user = User(name='tester', email='test@gmail.com', password=hashed_password, username='tester')
        test_session.add(user)
        test_session.commit()
        
        yield {'room': room.id, 'seat': seat.id, 'user': user.id}

# 服务器创建预定
@pytest.fixture(scope='function')
def test_booking(test_session, test_data):
    with app.app_context():        
        current = datetime.now()
        start_time = datetime(current.year, current.month, current.day, current.hour+1, 00)
        end_time = datetime(current.year, current.month, current.day, current.hour+2, 00)
        booking = Booking(seatid=test_data['seat'], userid=test_data['user'], starttime=start_time, finishtime=end_time, booktime=current)
        test_session.add(booking)
        test_session.commit()
        
        yield booking.id

# 客户端测试
@pytest.fixture(scope='function')
def test_client():
    with app.test_client() as testing_client:
        yield testing_client

# 测试新建座位预定
def test_create_booking(test_client, test_data):
    # 用户登录
    with test_client.session_transaction() as session:
        session['userid'] = test_data['user']
        
    # 测试预定座位
    start_time = datetime.now()
    end_time = start_time + timedelta(hours=1)

    response = test_client.post(
        '/booking/create',
        json={
            'seat_id': str(test_data['seat']),
            'start_time': start_time.strftime('%Y-%m-%d %H:%M:%S'),
            'end_time': end_time.strftime('%Y-%m-%d %H:%M:%S')
        },
    )
    assert response.json['status'] == 200

    book_id = response.json['data']
    
    # 检查是否成功预定座位
    bookings = Booking.query.filter_by(id=book_id).all()
    booking = bookings[0]
    assert booking.seatid == str(test_data['seat'])
    assert booking.starttime == start_time.strftime('%Y-%m-%d %H:%M:%S')
    assert booking.finishtime == end_time.strftime('%Y-%m-%d %H:%M:%S')
    
    # 测试预定同一座位的冲突时间段
    response = test_client.post(
        '/booking/create',
        json={
            'seat_id': str(test_data['seat']),
            'start_time': start_time.strftime('%Y-%m-%d %H:%M:%S'),
            'end_time': end_time.strftime('%Y-%m-%d %H:%M:%S')
        },
    )
    assert response.json['status'] == 535
    

# 测试查询预定记录
def test_get_bookings(test_client, test_data):
    # 用户登录
    with test_client.session_transaction() as session:
        session['userid'] = test_data['user']
    
    # 测试查询预定记录
    response = test_client.get(f'/booking/get_bookings')
    assert response.json['status'] == 200
    
    bookings = response.json['data']
    assert bookings[0]['seat_id'] == str(test_data['seat'])
        

# 测试取消预定
def test_cancel_booking(test_client, test_data, test_booking):
    # 用户登录
    with test_client.session_transaction() as session:
        session['userid'] = test_data['user']

    # 测试取消预定
    response = test_client.post('/booking/cancel', json={
        'booking_id': str(test_booking)
    })
    assert response.json['status'] == 200

    
    booking = Booking.query.filter_by(id=test_booking).all()[0]
    assert booking.iscancel == '1'

# 测试用户签到：在每个小时的30分前失败（未到签到时间），30分后成功
def test_checkin(test_client, test_data, test_booking):
    # 用户登录
    with test_client.session_transaction() as session:
        session['userid'] = test_data['user']

    # 测试用户签到
    response = test_client.post('/booking/checkin', json={
        'booking_id': str(test_booking)
    })

    assert response.json['status'] == 200
    
    
    booking = Booking.query.filter_by(id=test_booking).all()[0]
    assert booking.ischeckin == '1'