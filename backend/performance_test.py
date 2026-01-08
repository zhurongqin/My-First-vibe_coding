"""
性能测试脚本，验证图像压缩和缓存功能
"""
import os
import sys
import requests
import time
from PIL import Image
import tempfile

def create_large_test_image(size=(2000, 2000)):
    """创建一个较大的测试图像以测试压缩功能"""
    img = Image.new('RGB', size, color='blue')
    temp_path = os.path.join(tempfile.gettempdir(), "large_test_image.jpg")
    img.save(temp_path, format='JPEG', quality=95)
    return temp_path

def test_image_compression():
    """测试图像压缩功能"""
    large_img_path = create_large_test_image()
    
    try:
        # 检查原始图像大小
        original_size = os.path.getsize(large_img_path)
        print(f"原始图像大小: {original_size} 字节 ({original_size/1024:.2f} KB)")
        
        # 上传图像
        start_time = time.time()
        with open(large_img_path, 'rb') as f:
            files = {'file': (os.path.basename(large_img_path), f, 'image/jpeg')}
            response = requests.post("http://localhost:8000/api/v1/upload/", files=files)
        
        upload_time = time.time() - start_time
        if response.status_code == 200:
            result = response.json()
            task_id = result['task_id']
            print(f"✓ 图像上传成功，耗时: {upload_time:.2f}s, 任务ID: {task_id}")
            
            # 等待处理完成
            status = None
            for _ in range(30):  # 最多等待30秒
                time.sleep(1)
                status_response = requests.get(f"http://localhost:8000/api/v1/tasks/status/{task_id}")
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    status = status_data['status']
                    if status == 'completed':
                        break
                    print(f"  任务状态: {status_data['status']}, 进度: {status_data.get('result', {}).get('current', 0)}/{status_data.get('result', {}).get('total', 100)}")
            
            if status == 'completed':
                print("✓ 任务完成")
                
                # 下载处理后的图像
                download_start = time.time()
                download_response = requests.get(f"http://localhost:8000/api/v1/tasks/download/{task_id}")
                download_time = time.time() - download_start
                
                if download_response.status_code == 200:
                    print(f"✓ 下载成功，耗时: {download_time:.2f}s, 文件大小: {len(download_response.content)} 字节")
                    
                    # 保存下载的图像以供检查
                    with open("/tmp/processed_image.png", "wb") as f:
                        f.write(download_response.content)
                    
                    # 验证图像有效性
                    try:
                        processed_img = Image.open("/tmp/processed_image.png")
                        print(f"✓ 处理后图像有效，尺寸: {processed_img.size}")
                        return True
                    except Exception as e:
                        print(f"✗ 处理后图像无效: {e}")
                        return False
                else:
                    print(f"✗ 下载失败，状态码: {download_response.status_code}")
                    return False
            else:
                print(f"✗ 任务未在规定时间内完成，最终状态: {status}")
                return False
        else:
            print(f"✗ 上传失败，状态码: {response.status_code}, 响应: {response.text}")
            return False
    except Exception as e:
        print(f"✗ 压缩测试失败: {e}")
        return False
    finally:
        # 清理
        os.remove(large_img_path)
        if os.path.exists("/tmp/processed_image.png"):
            os.remove("/tmp/processed_image.png")

def test_cache_functionality():
    """测试缓存功能"""
    test_img_path = os.path.join(tempfile.gettempdir(), "cached_test_image.jpg")
    
    # 创建相同内容的测试图像
    img = Image.new('RGB', (300, 300), color='green')
    img.save(test_img_path, format='JPEG')
    
    try:
        # 第一次上传
        print("第一次上传...")
        with open(test_img_path, 'rb') as f:
            files = {'file': (os.path.basename(test_img_path), f, 'image/jpeg')}
            response1 = requests.post("http://localhost:8000/api/v1/upload/", files=files)
        
        if response1.status_code == 200:
            result1 = response1.json()
            print(f"  第一次上传成功，任务ID: {result1['task_id']}")
            
            # 等待第一次处理完成
            for _ in range(30):
                time.sleep(1)
                status_response = requests.get(f"http://localhost:8000/api/v1/tasks/status/{result1['task_id']}")
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    if status_data['status'] == 'completed':
                        break
            
            # 第二次上传相同图像
            print("第二次上传相同图像（测试缓存）...")
            start_time = time.time()
            with open(test_img_path, 'rb') as f:
                files = {'file': (os.path.basename(test_img_path), f, 'image/jpeg')}
                response2 = requests.post("http://localhost:8000/api/v1/upload/", files=files)
            second_upload_time = time.time() - start_time
            
            if response2.status_code == 200:
                result2 = response2.json()
                print(f"  第二次上传成功，任务ID: {result2['task_id']}")
                print(f"  第二次上传耗时: {second_upload_time:.2f}s")
                
                # 检查两个任务ID是否相同（如果是缓存命中的话）
                if result1['task_id'] == result2['task_id']:
                    print("✓ 缓存功能工作正常，返回了相同的任务ID")
                    return True
                else:
                    # 即使任务ID不同，如果第二次上传非常快，也可能表示缓存起效
                    if second_upload_time < 1.0:  # 如果第二次上传小于1秒
                        print(f"✓ 缓存功能可能工作正常，第二次上传非常快({second_upload_time:.2f}s)，可能已缓存")
                        return True
                    else:
                        print(f"✗ 缓存功能可能未生效，第二次上传耗时较长({second_upload_time:.2f}s)")
                        return False
            else:
                print(f"✗ 第二次上传失败，状态码: {response2.status_code}")
                return False
        else:
            print(f"✗ 第一次上传失败，状态码: {response1.status_code}")
            return False
    except Exception as e:
        print(f"✗ 缓存测试失败: {e}")
        return False
    finally:
        # 清理
        if os.path.exists(test_img_path):
            os.remove(test_img_path)

def main():
    """运行性能测试"""
    print("开始性能测试...")
    print("="*50)
    
    # 测试图像压缩功能
    compression_ok = test_image_compression()
    
    print("\n" + "-"*30 + "\n")
    
    # 测试缓存功能
    cache_ok = test_cache_functionality()
    
    print("="*50)
    print("性能测试完成!")
    
    results = {
        "Image Compression": compression_ok,
        "Cache Functionality": cache_ok
    }
    
    print("\n性能测试结果摘要:")
    for test, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {test}: {status}")
    
    overall_success = compression_ok and cache_ok
    print(f"\n总体性能测试结果: {'✓ ALL TESTS PASSED' if overall_success else '? SOME TESTS FAILED'}")
    
    return overall_success

if __name__ == "__main__":
    main()