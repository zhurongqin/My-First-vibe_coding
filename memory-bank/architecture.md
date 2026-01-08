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

## 文件架构说明

### 后端文件架构

#### 核心应用结构 (`/backend/app`)
- **main.py**: FastAPI应用的主入口文件，配置CORS、注册路由、设置中间件
  - 包含限流中间件，实现IP请求频率限制
  - 配置了全局错误处理机制
- **config.py**: 配置管理模块，定义了服务配置、Redis配置、文件上传配置、本地存储配置和API配置等
  - 包含HOST、PORT等服务配置项
  - 包含REDIS_HOST、REDIS_PORT等Redis连接配置
  - 包含MAX_FILE_SIZE、ALLOWED_FILE_TYPES等文件上传限制
  - 包含UPLOAD_FOLDER、OUTPUT_FOLDER等本地存储路径配置
  - 新增图像压缩配置项：COMPRESS_QUALITY（压缩质量）、COMPRESS_MAX_WIDTH（最大宽度）、COMPRESS_MAX_HEIGHT（最大高度）
- **rate_limit.py**: 限流模块，实现基于IP的请求频率限制，使用滑动窗口算法

#### Celery配置 (`/backend/app/celery_config.py`)
- **celery_config.py**: Celery应用配置文件，设置Redis为broker和result_backend，配置任务序列化、时区、路由等参数

#### 任务定义 (`/backend/app/tasks.py`)
- **compress_image**: 新增图像压缩函数，实现图像尺寸调整和质量压缩，支持保持宽高比
  - 自动检测图像类型并进行适当转换（如PNG透明背景转为白色背景）
  - 根据配置的最大宽高限制调整图像尺寸
  - 按设定的质量参数压缩JPEG图像
- **remove_background_task**: 核心异步任务，处理图像背景移除逻辑，包括文件读取、base64编码、API调用、结果保存等
  - 实现了重试机制（最多3次，间隔递增：1秒、3秒、5秒）
  - 集成外部抠图API（http://115.159.43.168:5000/api/remove-bg/base64）
  - 包含错误处理和模拟实现（当外部API不可用时的备用方案）
  - 增加了详细的日志记录，便于调试和监控
  - 实现了针对不同错误类型的处理（超时、连接错误、验证错误等）
  - 添加了恶意输入防护，使用PIL验证和清理图像，防止图像炸弹攻击
  - 实现了进度追踪功能，使用`self.update_state`更新任务进度
  - **新增**：集成图像压缩功能，在处理前自动压缩图像以优化性能
  - **新增**：在finally块中清理压缩产生的临时文件
- **validate_and_sanitize_image**: 图像验证和清理函数，使用PIL验证图像并限制最大像素数
- **simulate_api_response**: 模拟API响应，当外部API不可用时的备用方案
- **cleanup_old_files**: 清理旧文件任务，删除超过指定天数的上传和输出文件

#### API路由 (`/backend/app/api/v1`)
- **routes.py**: 
  - 上传路由：处理文件上传请求，验证文件类型和大小，启动异步任务
  - 上传路由现在包含缓存机制，通过文件内容哈希检查是否已处理过相同图像
  - 新增is_cached和cache_result函数，实现简单内存缓存系统
  - 缓存包含5分钟过期机制，防止内存无限增长
  - 上传路由现在会先检查缓存，如果命中则直接返回之前任务ID
  - 上传路由现在集成了图像压缩功能
  - 上传路由现在包含更详细的错误信息返回
- **task_routes.py**: 
  - 任务相关路由的专门处理文件
  - 状态查询路由：`GET /status/{task_id}`，查询任务处理状态，支持PROGRESS状态和进度信息
  - 结果获取路由：`GET /result/{task_id}`，获取处理结果
  - 下载路由：`GET /download/{task_id}`，提供处理后图像的下载
  - 清理路由：`POST /cleanup`，手动触发文件清理任务
  - 通过/tasks前缀注册到API中
- **__init__.py**: API路由器初始化文件，整合并注册所有子路由
  - 上传路由注册到 `/upload` 前缀下，形成 `/api/v1/upload/`
  - 任务路由注册到 `/tasks` 前缀下，形成 `/api/v1/tasks/*`

### 前端文件架构

#### 核心组件 (`/frontend/src`)
- **App.tsx**: React应用的主组件，应用的根节点
- **index.tsx**: React应用的入口文件，渲染App组件到DOM
- **index.css**: 全局样式定义

#### 组件 (`/frontend/src/components`)
- **UploadComponent.tsx**: 文件上传组件，提供拖拽上传和点击上传两种方式，包含文件类型和大小验证UI反馈
  - 实现了完整的上传流程：选择文件→上传→处理→结果展示
  - 添加了任务状态轮询机制，定期查询后端任务状态
  - 实现了进度指示，显示上传和处理进度
  - 添加了结果展示功能，处理完成后显示图像并提供下载
  - 增强了错误处理机制，包含错误提示、重试计数和用户友好的错误信息
  - 添加了重试计数器，限制最大重试次数为3次
  - 添加了加载动画，提升等待体验
  - 实现了结果预览功能，支持原始和处理后图像对比
  - 添加了重新处理选项，允许用户重新处理同一图像
  - 优化了界面响应速度
  - 实现了实时进度反馈，通过轮询获取任务进度状态
- **ImagePreview.tsx**: 图像预览组件，显示选择的图像，提供缩放和拖拽功能

#### API服务 (`/frontend/src/services/api.js`)
- **api.js**: 前端API客户端，封装了与后端API通信的方法
  - 上传图像方法：`uploadImage(file, onProgress)`，支持进度回调
  - 获取处理状态方法：`getProcessingStatus(taskId)`，查询任务状态
  - 获取处理结果方法：`getProcessingResult(taskId)`，获取处理结果

#### 配置 (`/frontend/src/config/api.js`)
- **api.js**: API配置文件，定义后端服务的基地址

### 测试与验证文件
- **test_upload_api.py**: 上传API功能验证脚本
- **test_celery_integration.py**: Celery集成验证脚本
- **test_external_api_integration.py**: 外部API集成验证脚本
- **debug_test.py**: 调试测试脚本
- **comprehensive_test.py**: 全面测试脚本，包含端到端功能测试、性能优化验证、安全机制确认和错误处理测试

### 环境检查与启动脚本 (`/backend`)
- **check_env.py**: 环境检查脚本，验证所有依赖正确安装
- **run_server.py**: 后端服务启动脚本
- **README.md**: 后端项目说明文档

### 项目文档 (`/memory-bank`)
- **implementation-plan.md**: 项目实施计划文档
- **progress.md**: 项目进度记录文档
- **architecture.md**: 系统架构文档（当前文件）
- **image_bg_remove-api.md**: 外部抠图API接口文档
- **image_bg_remove-design-document.md**: 系统设计文档
- **teach-stack.md**: 技术栈说明文档