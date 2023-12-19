# ibooking-flask
为了方便学生自习，学校开放了一批自习室。自习室中的座位利用率不高，经常出现一座难求，同时又有书包占座人却不在的情况。为了提升座位的利用率和周转率，学校一方面考虑动态调整自习室的数量，另一方面也希望采用信息技术手段提升座位的利用率。

本项目以高等学校日常学习生活为背景，通过python-flask框架和mysql数据库构建了一个自习室座位预约系统后端。与vue前端协同实现了用户注册登陆座位预定、管理员座位管理等功能，提升各类自习室座位使用率。
## 配置数据库

```
docker build -t mysql .
docker run -p 3306:3306 --name mysql-container -d mysql
```

## 配置环境
```
pip install -r ./requirements.txt
```

## 配置密钥
在根目录下新建setting.json，配置如下
```
{
    "db_connect":"mysql+pymysql://username:password@serverip",
    "mail":"your_mail_account",
    "mail_key":"your_mail_sercetkey"
}
```

## 启动Flask服务
```
python runserver.py
```

## 访问API文档
本项目提供了交互式API文档用于各个接口的功能说明和测试
```
http://localhost:5000/
```


