# 人参重金属检测溯源系统 - 后端镜像
FROM python:3.11-slim

WORKDIR /app

# 先装依赖（利用缓存层）
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制后端代码
COPY main.py .
COPY report_template.py .

# 数据库连接通过环境变量注入（DB_HOST/DB_USER/DB_PASSWORD/DB_NAME 等）
ENV DB_HOST=127.0.0.1 \
    DB_PORT=3306 \
    DB_USER=root \
    DB_PASSWORD=123456 \
    DB_NAME=ginseng_db

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
