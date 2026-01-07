"""
测试第9步：集成外部抠图API
"""
import requests
import time
import os
import base64

# 设置服务器地址
BASE_URL = 'http://localhost:8000'

# 使用 memory-bank 文件夹中的 111.jpeg 文件
test_file_path = 'memory-bank/111.jpeg'

try:
    print('开始测试外部API集成...')

    # 检查文件是否存在
    if not os.path.exists(test_file_path):
        print(f'文件不存在: {test_file_path}')
        exit(1)

    print(f'使用测试文件: {test_file_path}')
    
    # 获取文件大小
    file_size = os.path.getsize(test_file_path)
    print(f'文件大小: {file_size} 字节 ({file_size/1024:.2f} KB)')

    # 上传文件
    print('\n上传测试文件...')
    with open(test_file_path, 'rb') as f:
        files = {'file': ('111.jpeg', f, 'image/jpeg')}
        response = requests.post(f'{BASE_URL}/api/v1/upload/', files=files)

    if response.status_code != 200:
        print(f'上传失败，状态码: {response.status_code}')
        print(f'响应内容: {response.text}')
    else:
        response_data = response.json()
        task_id = response_data['task_id']
        print(f'上传成功，获取到任务ID: {task_id}')

        # 轮询任务状态
        print('\n轮询任务状态...')
        max_attempts = 60  # 增加轮询次数以应对大文件处理时间
        for i in range(max_attempts):
            time.sleep(2)  # 增加轮询间隔
            status_response = requests.get(f'{BASE_URL}/api/v1/status/{task_id}')
            if status_response.status_code == 200:
                status_data = status_response.json()
                print(f'   状态: {status_data["status"]}, 消息: {status_data["message"]}')
                
                if status_data['status'] in ['completed', 'failed']:
                    print(f'任务完成，最终状态: {status_data["status"]}')
                    break
            else:
                print(f'状态查询失败，状态码: {status_response.status_code}')

finally:
    print('\n测试完成')