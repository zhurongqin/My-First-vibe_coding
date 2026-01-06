import subprocess
import sys
import os
from app.config import settings

def install_dependencies():
    """安装项目依赖"""
    print("正在安装后端依赖...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    print("依赖安装完成")

def run_server():
    """运行后端服务"""
    print(f"启动服务器，监听 {settings.HOST}:{settings.PORT}")
    
    # 导入并运行FastAPI应用
    import uvicorn
    from app.main import app
    
    uvicorn.run(
        app,
        host=settings.HOST,
        port=settings.PORT,
        reload=True  # 开发模式下自动重载
    )

if __name__ == "__main__":
    # 检查是否需要安装依赖
    if len(sys.argv) > 1 and sys.argv[1] == "--install":
        install_dependencies()
    
    # 确保必要目录存在
    os.makedirs(settings.UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(settings.OUTPUT_FOLDER, exist_ok=True)
    
    # 运行服务器
    run_server()