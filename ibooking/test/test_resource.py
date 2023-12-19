import pytest
from ibooking import app, db
from ibooking.models import Room, Seat, Booking, User
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

# 服务器数据事务
@pytest.fixture(scope='module')
def test_data(test_session):
    with app.app_context():        
        test_session.begin_nested()
        
        room = Room(number='test', latitude=30.1234, longitude=120.5678, maxvolume=50, note='7:00-22:00')
        roomd = Room(number='testd', latitude=30.1234, longitude=120.5678, maxvolume=50, note='7:00-22:00')
        test_session.add(room)
        test_session.add(roomd)
        test_session.commit()

        seat = Seat(number='test01', roomid=room.id, isdisabled = '0')
        test_session.add(seat)
        test_session.commit()
        
        initial_password = '123456'
        hashed_password = generate_password_hash('123456', method='sha256')
        user = User(name='tester1', email='test1@gmail.com', password=hashed_password, username='tester1')
        test_session.add(user)
        test_session.commit()
        
        yield {'roomd':roomd.number, 'room_id':room.id, 'room_number': room.number,'room_latitude':room.latitude, 'room_longitude':room.longitude, 'room_maxvolume':room.maxvolume, 'room_note':room.note,
                'seat_id':seat.id, 'seat_roomid':seat.roomid, 'seat_number': seat.number, 'seat_ischarge':seat.ischarge, 'seat_isdisabled':seat.isdisabled,
                'user_id': user.id, 'user_name':user.name, 'user_password':initial_password, 'user_email':user.email, 'user_username':user.username}
        
        test_session.rollback()

@pytest.fixture(scope='function')
def test_client():
    with app.test_client() as testing_client:
        yield testing_client

def test_register(test_client, test_data):
    # 测试注册用户
    response = test_client.post(
        '/user/register',
        json={
            'name':'test_user',
            'email':'test_email',
            'password':'test_password',
            'username':'test_username'
        },
    )
    assert response.json['status'] == 200

    userid = response.json['data']

    users = User.query.filter_by(id = userid).all()
    user = users[0]
    assert user.name == 'test_user'
    assert user.email == 'test_email'
    assert check_password_hash(user.password,'test_password')
    assert user.username == 'test_username'

def test_login(test_client, test_data):
    # 测试用户登录
    response = test_client.post(
        '/user/login',
        json={
            'password':str(test_data['user_password']),
            'username':str(test_data['user_username'])
        }
    )

    assert response.json['status'] == 200

    user_id = response.json['data']

    users = User.query.filter_by(id = user_id).all()
    user = users[0]
    assert check_password_hash(user.password, str(test_data['user_password']))
    assert user.username == str(test_data['user_username'])

def test_logout(test_client,test_data):
        with test_client.session_transaction() as session:
            session['userid'] = test_data['user_id']
        
        # 测试登出
        response = test_client.post(
            '/user/logout',
            json={},
        )
        assert response.json['status'] == 200

def test_addroom(test_client,test_data):
    # 测试添加自习室
    response = test_client.post(
        '/resource/addroom',
        json={
            'number':'A01',
            'latitude':1.2,
            'longitude':2.1,
            'maxvolume':20,
            'note':'7:00-22:00'
        },
    )

    assert response.json['status'] == 200

def test_deleteroom(test_client,test_data):
    # 测试删除自习室
    response = test_client.post(
        '/resource/deleteroom',
        json={
            'number':str(test_data['roomd'])
        },
    )

    assert response.json['status'] == 200

def test_modifyroom(test_client,test_data):
    # 测试修改自习室
    response = test_client.post(
        'resource/modifyroom',
        json={
            'id':str(test_data['room_id']),
            'number':str(test_data['room_number']),
            'latitude':test_data['room_latitude'],
            'longitude':test_data['room_longitude'],
            'maxvolume':test_data['room_maxvolume']
        },
    )

    assert response.json['status'] == 200

def test_modifyseat(test_client,test_data):
    # 测试修改座位
    response = test_client.post(
        '/resource/modifyseat',
        json={
            'id':str(test_data['seat_id']),
            'isdisabled':str(test_data['seat_isdisabled']),
            'number':str(test_data['seat_number']),
            'ischarge':str(test_data['seat_ischarge'])
        },
    )

    assert response.json['status'] == 200

def test_getroom(test_client,test_data):
    # 测试查询自习室
    response = test_client.get(f'/resource/getroom')
    assert response.json['status'] == 200

    rooms = response.json['data']
    for i in range(len(rooms)):
        if rooms[i]['id'] == test_data['room_id']:
            room = rooms[i]
    assert room['number'] == test_data['room_number']

def test_getseat(test_client,test_data):
    # 测试查询座位
    response = test_client.get(f'/resource/getseat')
    assert response.json['status'] == 200

    seats = response.json['data']
    for i in range(len(seats)):
        if seats[i]['id'] == test_data['seat_id']:
            seat = seats[i]
    assert seat['number'] == test_data['seat_number']
