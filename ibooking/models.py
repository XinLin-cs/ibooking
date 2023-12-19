from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from flask_sqlalchemy import SQLAlchemy
from ibooking import db


class User(db.Model):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(45))
    email = Column(String(45))
    password = Column(String(100))
    username = Column(String(45))

    def to_dict(self):
        return {'id': self.id, 'name': self.name, 'email': self.email}
    
class Room(db.Model):
    __tablename__ = 'room'

    id = Column(Integer, primary_key=True)
    number = Column(String(45))
    latitude = Column(Float)
    longitude = Column(Float)
    maxvolume = Column(Integer)
    note = Column(String(45))
    
    def to_dict(self):
        return {'id':self.id, 'number': self.number, 'latitude':self.latitude, 'longitude':self.longitude, 'maxvolume':self.maxvolume}

class Seat(db.Model):
    __tablename__ = 'seat'

    id = Column(Integer, primary_key=True)
    roomid = Column(String(45))
    number = Column(String(45))
    ischarge = Column(String(45))
    isdisabled = Column(String(45))
    freetime = Column(String(45))
    usingtime = Column(String(45))
    bookedtime = Column(String(45))

    def to_dict(self):
        return {'id':self.id, 'number': self.number, 'roomid':self.roomid, 'ischarge':self.ischarge, 'isdisabled':self.isdisabled}


class Booking(db.Model):
    __tablename__ = 'booking'

    id = Column(Integer, primary_key=True)
    seatid = Column(String(45))
    userid = Column(String(45))
    booktime = Column(String(45))
    starttime = Column(String(45))
    finishtime = Column(String(45))
    isdefault = Column(String(45))
    iscancel = Column(String(45))
    ischeckin = Column(String(45))