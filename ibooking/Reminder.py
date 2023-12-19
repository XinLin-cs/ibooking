from ibooking import models
from datetime import datetime, timedelta
from ibooking import app, db, mail
from ibooking.models import Booking
from flask_mail import Message
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler(daemon=True)

# 签到提醒
@scheduler.scheduled_job('cron', minute='45')
def checkin_reminder():
    with app.app_context():
        # 获取当前时间的小时和分钟
        current_time = datetime.now()

        # 计算需要提醒的时间段
        start_time = datetime(current_time.year, current_time.month, current_time.day, current_time.hour+1, 0, 0)

        # 查询需要提醒的预定记录
        bookings = Booking.query.filter(Booking.starttime == start_time, Booking.ischeckin=='0', Booking.iscancel=='0', Booking.isdefault=='0').all()
        
        # 发送提醒邮件
        print('[scheduler] searching CHECKIN: there are %d bookings start after 15 min'%(len(bookings)))
        for booking in bookings:
            user = models.User.query.filter_by(id=booking.userid).first()
            email = user.email
            msg = Message('[ibooking] Your booking is check-in now', sender='fudan_ibooking@126.com', recipients=[email])
            msg.body = f'Yours booking(ID: {booking.id}) will start after 15 minutes, Pay attention to early check-in.(this is a system mail, do not reply.)'
            mail.send(msg)

            print('[scheduler] 签到提醒邮件已发送！')

# 二次签到、即将违约提醒
@scheduler.scheduled_job('cron', minute='10')
def checkin_reminder():
    with app.app_context():
        # 获取当前时间的小时和分钟
        current_time = datetime.now()

        # 计算需要提醒的时间段
        start_time = datetime(current_time.year, current_time.month, current_time.day, current_time.hour, 0, 0)

        # 查询需要提醒的预定记录
        bookings = Booking.query.filter(Booking.starttime == start_time, Booking.ischeckin=='0', Booking.iscancel=='0', Booking.isdefault=='0').all()

        # 发送提醒邮件
        print('[scheduler] searching DELAY: there are %d bookings delay 10 min'%(len(bookings)))
        for booking in bookings:
            user = models.User.query.filter_by(id=booking.userid).first()
            email = user.email
            msg = Message('[ibooking] Your booking is check-in now', sender='fudan_ibooking@126.com', recipients=[email])
            msg.body = f'Yours booking(ID: {booking.id}) has started for 10 min, it will cause default after 5 min, Pay attention to check-in.(this is a system mail, do not reply.)'
            mail.send(msg)

            print('[scheduler] 即将违约提醒邮件已发送！')

# 违约提醒
@scheduler.scheduled_job('cron', minute='15')
def check_default_bookings():
    with app.app_context():
        # 获取当前时间的小时和分钟
        current_time = datetime.now()

        # 计算需要提醒的时间段
        start_time = datetime(current_time.year, current_time.month, current_time.day, current_time.hour, 0, 0)

        # 查询需要提醒的预定记录
        bookings = Booking.query.filter(Booking.starttime == start_time, Booking.ischeckin=='0', Booking.iscancel=='0', Booking.isdefault=='0').all()
        
        # 记录违约
        for booking in bookings:
            booking.isdefault = '1'
        db.session.commit()
        
        # 发送提醒邮件
        print('[scheduler] searching DEFAULT: there are %d bookings delay 15 min'%(len(bookings)))    
        for booking in bookings:      
            user = models.User.query.filter_by(id=booking.userid).first()
            email = user.email
            msg = Message('[ibooking] Your booking becoming a default!', sender='fudan_ibooking@126.com', recipients=[email])
            msg.body = f'Yours booking(ID: {booking.id}) is becoming a default due to the 15 min delay. Please contact to the manager if you have any question.(this is a system mail, do not reply.)'
            mail.send(msg)

            print('[scheduler] 违约提醒邮件已发送！')