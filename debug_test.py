"""
调试测试脚本：检查外部API集成中的异常
"""
import requests
import time
import os

# 设置服务器地址
BASE_URL = "http://localhost:8005"

def debug_test():
    """调试测试"""
    print("开始调试测试...")
    
    # 创建一个临时测试文件 - 使用更简单的JPEG格式
    test_file_path = "test_image.jpg"
    
    # 创建一个最小化的JPEG文件（包含基本的JPEG头信息）
    jpeg_content = b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00' \
                   b'\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c' \
                   b'\x19\x12\x13\x0f\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xc0\x00\x11\x08\x00\x01' \
                   b'\x00\x01\x01\x01\x11\x00\x02\x11\x01\x03\x11\x01\xff\xc4\x00\x14\x10\x01\x00' \
                   b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\xff\xc4\x00\x14' \
                   b'\x11\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xda\x00\x08' \
                   b'\x01\x01\x00\x01\x05\x02\xff\xd9'
    
    with open(test_file_path, "wb") as f:
        f.write(jpeg_content)
    
    try:
        # 1. 首先测试健康检查
        print("\n1. 测试健康检查端点...")
        health_response = requests.get(f"{BASE_URL}/health")
        print(f"健康检查响应: {health_response.status_code}, {health_response.json()}")
        
        # 2. 测试API文档路径
        print("\n2. 测试API文档路径...")
        api_docs = requests.get(f"{BASE_URL}/api/v1")
        print(f"API文档响应: {api_docs.status_code}")
        
        # 3. 上传文件
        print("\n3. 上传测试文件...")
        with open(test_file_path, "rb") as f:
            files = {"file": (test_file_path, f, "image/jpeg")}
            response = requests.post(f"{BASE_URL}/api/v1/upload/", files=files)
        
        print(f"上传响应状态码: {response.status_code}")
        print(f"上传响应内容: {response.json()}")
        
        if response.status_code != 200:
            print("✗ 上传失败")
            return False
        
        response_data = response.json()
        if "task_id" not in response_data:
            print("✗ 响应中没有task_id")
            return False
        
        task_id = response_data["task_id"]
        print(f"获取到任务ID: {task_id}")
        
        # 4. 直接访问状态端点进行测试
        print("\n4. 直接访问状态端点...")
        status_url = f"{BASE_URL}/api/v1/status/{task_id}"
        print(f"访问URL: {status_url}")
        
        status_response = requests.get(status_url)
        print(f"状态响应状态码: {status_response.status_code}")
        print(f"状态响应内容: {status_response.text}")
        
        # 5. 如果状态端点返回404，检查所有路由
        print("\n5. 检查路由注册...")
        # 检查OpenAPI文档
        openapi_response = requests.get(f"{BASE_URL}/openapi.json")
        if openapi_response.status_code == 200:
            openapi = openapi_response.json()
            paths = list(openapi.get("paths", {}).keys())
            print(f"注册的路径: {paths}")
        
        return True
            
    except Exception as e:
        print(f"✗ 测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # 清理测试文件
        if os.path.exists(test_file_path):
            os.remove(test_file_path)
            print(f"\n已删除测试文件: {test_file_path}")

if __name__ == "__main__":
    debug_test()