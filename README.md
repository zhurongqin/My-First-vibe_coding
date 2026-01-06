# 图像背景移除Web应用

一个基于AI技术的图像背景移除Web应用，允许用户上传图片并自动移除图片背景。

## 项目结构

```
image_bg_remove_web/
├── frontend/           # React前端项目
│   ├── public/
│   ├── src/
│   ├── package.json
│   └── ...
├── backend/            # FastAPI后端项目
│   ├── app/
│   ├── requirements.txt
│   └── ...
├── memory-bank/        # 项目文档和设计
│   ├── implementation-plan.md
│   ├── progress.md
│   └── ...
└── README.md
```

## 技术栈

- **前端**: React + TypeScript
- **后端**: FastAPI (Python)
- **异步任务**: Celery + Redis
- **图像处理**: Pillow + 计划集成RemBG等AI模型

## 开发环境配置

### 后端配置

1. 安装Python依赖:

```bash
cd backend
pip install -r requirements.txt
```

2. 配置环境变量:

```bash
cp .env.example .env
```

3. 启动后端服务:

```bash
python run_server.py
```

### 前端配置

1. 安装Node.js依赖:

```bash
cd frontend
npm install
```

2. 启动前端开发服务器:

```bash
npm start
```

## 开发进度

- [x] 第1步：项目初始化
- [x] 第2步：配置开发环境
- [ ] 第3步：建立基础API路由
- [ ] ...

## 项目规划

详细实施计划见 [implementation-plan.md](memory-bank/implementation-plan.md)

## 运行环境检查

可以使用以下命令验证开发环境配置:

```bash
# 后端环境检查
cd backend
python check_env.py
```

## 部署说明

- 前端、后端、抠图API均部署在同一服务器
- 使用服务器本地存储替代OSS服务
- 部署时需要配置Redis服务支持Celery异步任务