FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目代码
COPY . .

# 创建数据目录
RUN mkdir -p data/papers data/chroma_db

# 暴露端口
EXPOSE 8000 8501

# 启动命令（默认启动 FastAPI）
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
