"""
测试脚本：验证Celery异步任务队列集成
"""
import requests
import time
import os

# 设置服务器地址
BASE_URL = "http://localhost:8001"

def test_celery_integration():
    """测试Celery集成"""
    print("开始测试Celery集成...")
    
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
        # 上传文件
        print("上传测试文件...")
        with open(test_file_path, "rb") as f:
            files = {"file": (test_file_path, f, "image/jpeg")}
            response = requests.post(f"{BASE_URL}/api/v1/upload/", files=files)
        
        print(f"上传响应状态码: {response.status_code}")
        
        if response.status_code != 200:
            print(f"✗ 上传失败，状态码: {response.status_code}")
            print(f"响应内容: {response.text}")
            return False
        
        response_data = response.json()
        print(f"上传响应: {response_data}")
        
        if "task_id" not in response_data:
            print("✗ 响应中没有task_id")
            return False
        
        task_id = response_data["task_id"]
        print(f"获取到任务ID: {task_id}")
        
        # 检查任务状态
        print("轮询任务状态...")
        for i in range(10):  # 最多检查10次
            time.sleep(2)  # 等待2秒
            status_response = requests.get(f"{BASE_URL}/api/v1/status/{task_id}")
            print(f"状态响应: {status_response.json()}")
            
            status_data = status_response.json()
            if status_data["status"] in ["completed", "failed"]:
                print(f"任务结束，状态: {status_data['status']}")
                break
        
        if status_data["status"] == "completed":
            print("✓ Celery集成测试通过")
            return True
        elif status_data["status"] == "failed":
            print(f"✗ 任务执行失败: {status_data.get('error', 'Unknown error')}")
            return False
        else:
            print(f"✗ 任务未在预期时间内完成，当前状态: {status_data['status']}")
            return False
            
    except Exception as e:
        print(f"✗ 测试过程中发生错误: {str(e)}")
        return False
    finally:
        # 清理测试文件
        if os.path.exists(test_file_path):
            os.remove(test_file_path)
            print(f"已删除测试文件: {test_file_path}")

def test_health_check():
    """测试健康检查端点"""
    print("\n开始测试健康检查端点...")
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if "status" in data and data["status"] == "healthy":
                print("✓ 健康检查测试通过")
                return True
            else:
                print("✗ 健康检查响应格式不正确")
                return False
        else:
            print(f"✗ 健康检查返回错误状态码: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ 测试健康检查时发生错误: {str(e)}")
        return False

if __name__ == "__main__":
    print("开始测试Celery异步任务队列集成...")
    print(f"测试服务器地址: {BASE_URL}")
    
    success = True
    success &= test_health_check()
    success &= test_celery_integration()
    
    if success:
        print("\n✓ 所有测试通过！")
    else:
        print("\n✗ 部分测试失败！")