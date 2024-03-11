# 使用官方Python运行时作为基础镜像
FROM python:3.9-slim-bullseye

# 设置工作目录
WORKDIR /app

# 将当前目录的文件复制到容器的/app目录
COPY . /app

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 设置容器的入口点为python bot.py
ENTRYPOINT ["python", "bot.py"]
