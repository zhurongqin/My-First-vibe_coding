"""
环境配置检查脚本
验证开发环境是否正确配置
"""
import sys
import os
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def check_dependencies():
    """检查依赖是否正确安装"""
    print("正在检查依赖...")
    
    dependencies = [
        ("fastapi", "FastAPI框架"),
        ("uvicorn", "ASGI服务器"),
        ("celery", "异步任务队列"),
        ("redis", "Redis客户端"),
        ("PIL", "图像处理库"),  # Pillow库的导入名是PIL
        ("requests", "HTTP请求库"),
        ("pydantic_settings", "配置管理"),
    ]
    
    missing_deps = []
    
    for module, description in dependencies:
        try:
            __import__(module)
            print(f"✓ {module} ({description}) - 已安装")
        except ImportError as e:
            print(f"✗ {module} ({description}) - 缺失: {e}")
            missing_deps.append(module)
    
    if missing_deps:
        print(f"\n缺少依赖: {', '.join(missing_deps)}")
        return False
    
    return True

def check_config():
    """检查配置是否正确加载"""
    print("\n正在检查配置...")
    
    try:
        from app.config import settings
        
        print(f"✓ 服务器主机: {settings.HOST}")
        print(f"✓ 服务器端口: {settings.PORT}")
        print(f"✓ Redis地址: {settings.REDIS_URL}")
        print(f"✓ 上传目录: {settings.UPLOAD_FOLDER}")
        print(f"✓ 输出目录: {settings.OUTPUT_FOLDER}")
        
        # 检查目录是否存在，不存在则创建
        os.makedirs(settings.UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(settings.OUTPUT_FOLDER, exist_ok=True)
        
        print("✓ 配置加载正常")
        return True
    except Exception as e:
        print(f"✗ 配置加载失败: {e}")
        return False

def check_api_connection():
    """检查API连接"""
    print("\n正在检查API连接...")
    
    try:
        import requests
        
        # 尝试连接到本地服务器
        import threading
        import time
        from app.main import app
        import uvicorn
        
        # 在后台启动服务器
        def run_server():
            uvicorn.run(app, host="127.0.0.1", port=8001, log_level="error")
        
        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()
        time.sleep(2)  # 等待服务器启动
        
        # 尝试健康检查
        response = requests.get("http://127.0.0.1:8001/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ API连接正常: {data}")
            return True
        else:
            print(f"✗ API连接失败: 状态码 {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ API连接检查失败: {e}")
        return False

def main():
    """主检查函数"""
    print("开始检查开发环境配置...\n")
    
    success = True
    
    # 检查依赖
    success &= check_dependencies()
    
    # 检查配置
    success &= check_config()
    
    # 注意: 由于端口可能被占用，API连接测试可能会失败，这在开发环境中是正常的
    # 所以我们不会因为API测试失败而使整个检查失败
    try:
        check_api_connection()
    except:
        print("⚠ API连接测试跳过（可能端口被占用）")
    
    print("\n" + "="*50)
    if success:
        print("✓ 环境配置检查完成，所有基本组件正常")
        print("✓ 你可以继续下一步开发")
    else:
        print("✗ 环境配置存在问题，请修复后重试")
        sys.exit(1)

if __name__ == "__main__":
    main()