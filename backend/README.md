# 图像背景移除后端服务

本项目是图像背景移除Web应用的后端服务，基于FastAPI框架开发。

## 功能特性

- 图像上传接口
- 异步图像处理（基于Celery）
- 健康检查端点
- 配置管理

## 技术栈

- FastAPI: Web框架
- Celery: 异步任务队列
- Redis: 任务队列存储
- Pillow: 图像处理
- Pydantic: 数据验证和配置管理

## 快速开始

### 环境要求

- Python 3.9+
- Redis 服务

### 安装依赖

```bash
pip install -r requirements.txt
```

### 配置

复制环境变量文件：

```bash
cp .env.example .env
```

根据需要修改 `.env` 文件中的配置。

### 启动服务

```bash
python run_server.py
```

服务将启动在 `http://localhost:8000`

### API端点

- `GET /`: 服务状态检查
- `GET /health`: 健康检查
- `POST /api/v1/upload`: 图像上传（待实现）

## 开发

运行环境检查：

```bash
python check_env.py
```

## 部署

在生产环境中，建议使用进程管理器（如Supervisor）或容器化部署。