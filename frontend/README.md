# 图像背景移除前端应用

本项目是图像背景移除Web应用的前端部分，使用React构建。

## 功能特性

- 图像上传界面
- 图像预览功能
- 与后端API交互
- 处理进度显示

## 技术栈

- React: 前端框架
- TypeScript: 类型检查
- React Scripts: 构建工具
- Webpack: 模块打包

## 快速开始

### 环境要求

- Node.js 14+
- npm 或 yarn

### 安装依赖

```bash
npm install
```

### 配置

环境变量在 `.env` 文件中配置，主要设置API服务器地址：

```bash
REACT_APP_API_BASE_URL=http://localhost:8000
```

### 启动开发服务器

```bash
npm start
```

应用将在 `http://localhost:3000` 上启动。

### 构建生产版本

```bash
npm run build
```

## 主要组件

- `Api`: 与后端API交互的客户端
- `Upload`: 文件上传组件
- `Preview`: 图像预览组件

## API集成

前端通过 `services/api.js` 与后端服务交互，包括：

- 健康检查
- 文件上传
- 处理进度查询