# 使用基础镜像
#FROM python:3.9-alpine
FROM python:3.9

# 设置工作目录
WORKDIR /app

# 将项目文件复制到镜像中
COPY . /app

# 安装依赖
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple &&  \
    pip install --no-cache-dir -r requirements.txt

# 暴露端口
EXPOSE 5000

# 设置环境变量
ENV FLASK_APP=runserver.py

# 启动应用程序
CMD ["flask", "run", "--host=0.0.0.0"]