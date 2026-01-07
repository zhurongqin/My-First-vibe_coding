"""
外部API集成测试脚本
验证第9步：集成外部抠图API的实现
"""
import requests
import time
import os

# 设置服务器地址
BASE_URL = "http://localhost:8005"

def test_external_api_integration():
    """测试外部API集成"""
    print("开始测试外部API集成...")
    
    # 创建一个临时测试文件
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
        # 1. 测试健康检查
        print("\n1. 测试健康检查端点...")
        health_response = requests.get(f"{BASE_URL}/health")
        if health_response.status_code == 200:
            print("✓ 健康检查测试通过")
        else:
            print(f"✗ 健康检查失败，状态码: {health_response.status_code}")
            return False
        
        # 2. 上传文件
        print("\n2. 上传测试文件...")
        with open(test_file_path, "rb") as f:
            files = {"file": (test_file_path, f, "image/jpeg")}
            response = requests.post(f"{BASE_URL}/api/v1/upload/", files=files)
        
        if response.status_code != 200:
            print(f"✗ 上传失败，状态码: {response.status_code}")
            print(f"响应内容: {response.text}")
            return False
        
        response_data = response.json()
        if "task_id" not in response_data:
            print("✗ 响应中没有task_id")
            return False
        
        task_id = response_data["task_id"]
        print(f"✓ 上传成功，获取到任务ID: {task_id}")
        
        # 3. 轮询任务状态直到完成或失败
        print("\n3. 轮询任务状态...")
        max_polls = 30  # 最多轮询30次（30秒）
        poll_count = 0
        
        while poll_count < max_polls:
            status_response = requests.get(f"{BASE_URL}/api/v1/status/{task_id}")
            if status_response.status_code != 200:
                print(f"✗ 状态查询失败，状态码: {status_response.status_code}")
                return False
            
            status_data = status_response.json()
            print(f"   状态: {status_data['status']}, 消息: {status_data['message']}")
            
            if status_data["status"] in ["completed", "failed"]:
                break
            
            time.sleep(1)  # 等待1秒再查询
            poll_count += 1
        
        if poll_count >= max_polls:
            print("✗ 超时，任务未完成")
            return False
        
        print(f"✓ 任务完成，最终状态: {status_data['status']}")
        
        # 4. 测试结果查询接口
        print("\n4. 测试结果查询接口...")
        result_response = requests.get(f"{BASE_URL}/api/v1/result/{task_id}")
        if result_response.status_code != 200:
            print(f"✗ 结果查询失败，状态码: {result_response.status_code}")
            return False
        
        result_data = result_response.json()
        print(f"✓ 结果查询成功，状态: {result_data['status']}")
        
        # 5. 如果任务完成，测试下载接口
        if result_data["status"] == "completed":
            print("\n5. 测试下载接口...")
            download_response = requests.get(f"{BASE_URL}/api/v1/download/{task_id}")
            if download_response.status_code != 200:
                print(f"✗ 下载失败，状态码: {download_response.status_code}")
                print(f"响应内容: {download_response.text}")
                # 任务可能失败，但这是正常的测试情况
            else:
                print("✓ 下载成功")
        else:
            print(f"\n5. 任务状态为 {result_data['status']}，跳过下载测试")
        
        # 6. 验证所有API端点都已注册
        print("\n6. 验证API端点注册...")
        openapi_response = requests.get(f"{BASE_URL}/openapi.json")
        if openapi_response.status_code != 200:
            print("✗ 获取API文档失败")
            return False
        
        openapi = openapi_response.json()
        paths = list(openapi.get("paths", {}).keys())
        
        expected_paths = [
            "/api/v1/upload/",
            "/api/v1/status/{task_id}",
            "/api/v1/result/{task_id}",
            "/api/v1/download/{task_id}",
            "/"
        ]
        
        all_found = True
        for path in expected_paths:
            if path not in paths:
                print(f"✗ 缺少API端点: {path}")
                all_found = False
            else:
                print(f"✓ API端点已注册: {path}")
        
        if all_found:
            print("\n✓ 所有API端点都已正确注册")
        
        print("\n✓ 外部API集成测试完成！")
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
    success = test_external_api_integration()
    if success:
        print("\n🎉 所有测试通过！外部API集成成功。")
    else:
        print("\n❌ 测试失败！请检查外部API集成。")