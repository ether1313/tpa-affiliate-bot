# 使用官方 Python 镜像
FROM python:3.10-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖（Pillow 会用到）
RUN apt-get update && apt-get install -y \
    python3-dev \
    libjpeg-dev \
    zlib1g-dev \
    && apt-get clean

# 复制 requirements.txt 并预先安装
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# 复制整个项目文件
COPY . .

# Fly.io 容器会自动运行以下指令
CMD ["python", "main_bot.py"]
