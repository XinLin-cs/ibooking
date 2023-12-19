"""
This script runs the application using a development server.
"""
from os import environ
from ibooking import app

if __name__ == '__main__':
    # 启动服务
    HOST = environ.get('SERVER_HOST', 'localhost')
    try:
        PORT = int(environ.get('SERVER_PORT', '5000'))
    except ValueError:
        PORT = 5000
    app.run(HOST, PORT, debug=True)