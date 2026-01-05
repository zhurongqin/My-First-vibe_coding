# 系统架构文档

## 项目结构

### 前端 (React)
- **目录**: `/frontend`
- **技术栈**: React, TypeScript, Tailwind CSS
- **作用**: 提供用户界面，处理图像上传和结果显示

### 后端 (FastAPI)
- **目录**: `/backend`
- **技术栈**: Python, FastAPI, Celery
- **作用**: 处理API请求，管理异步任务，与抠图服务API交互

### 配置文件
- **.gitignore**: 指定Git版本控制忽略的文件和目录
- **requirements.txt**: Python依赖列表
- **package.json**: 前端项目配置和依赖

### 架构图
```
前端 (React) → 后端 (FastAPI) → 抠图服务API → 本地存储
```

### 任务处理流程
```
用户上传图像 → FastAPI接收 → Celery异步处理 → 调用抠图服务API → 处理完成 → 保存到本地存储 → 前端获取结果
```