# 使用官方Python运行时作为父镜像
FROM registry.cn-hangzhou.aliyuncs.com/sh-lijian/python:3.12.7-slim

# 设置工作目录
WORKDIR /app

# 复制项目文件到工作目录
COPY requirements*.txt /app

# 安装项目依赖
RUN pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt && pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements-wechat.txt

# 设置环境变量
ENV PYTHONUNBUFFERED=1

# 暴露端口8080
EXPOSE 8080

# 运行应用
# Start of Selection
CMD ["python", "app.py"]
# End of Selection