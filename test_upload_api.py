"""
测试脚本：验证文件上传API功能
"""
import requests
import os

# 设置服务器地址
BASE_URL = "http://localhost:8001"

def test_upload_api():
    """测试上传API功能"""
    print("开始测试上传API...")
    
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
    
    # 测试上传文件
    try:
        with open(test_file_path, "rb") as f:
            files = {"file": (test_file_path, f, "image/jpeg")}
            response = requests.post(f"{BASE_URL}/api/v1/upload/", files=files)
            
        print(f"响应状态码: {response.status_code}")
        print(f"响应内容: {response.json()}")
        
        # 验证响应
        if response.status_code == 200:
            data = response.json()
            if "upload_id" in data and "message" in data and data["message"] == "文件上传成功":
                print("✓ 上传API测试通过")
            else:
                print("✗ 上传API响应格式不正确")
        else:
            print(f"✗ 上传API返回错误状态码: {response.status_code}")
    except Exception as e:
        print(f"✗ 测试上传API时发生错误: {str(e)}")
    
    # 清理测试文件
    if os.path.exists(test_file_path):
        os.remove(test_file_path)
        print(f"已删除测试文件: {test_file_path}")

def test_file_type_validation():
    """测试文件类型验证"""
    print("\n开始测试文件类型验证...")
    
    # 创建一个非图像文件用于测试
    test_file_path = "test_file.txt"
    with open(test_file_path, "w") as f:
        f.write("This is a test file that should be rejected by the API")
    
    try:
        with open(test_file_path, "rb") as f:
            files = {"file": (test_file_path, f, "text/plain")}
            response = requests.post(f"{BASE_URL}/api/v1/upload/", files=files)
            
        print(f"响应状态码: {response.status_code}")
        
        # 应该返回400错误
        if response.status_code == 400:
            print("✓ 文件类型验证测试通过")
        else:
            print(f"✗ 文件类型验证失败，期望状态码400，实际得到: {response.status_code}")
    except Exception as e:
        print(f"✗ 测试文件类型验证时发生错误: {str(e)}")
    
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
            else:
                print("✗ 健康检查响应格式不正确")
        else:
            print(f"✗ 健康检查返回错误状态码: {response.status_code}")
    except Exception as e:
        print(f"✗ 测试健康检查时发生错误: {str(e)}")

if __name__ == "__main__":
    print("开始测试文件上传API功能...")
    print(f"测试服务器地址: {BASE_URL}")
    
    test_health_check()
    test_upload_api()
    test_file_type_validation()
    
    print("\n所有测试完成！")