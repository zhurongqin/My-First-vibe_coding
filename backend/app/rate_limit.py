import time
from collections import defaultdict
from fastapi import HTTPException
from .config import settings

# 使用字典存储每个IP的请求记录
ip_requests = defaultdict(list)

def check_rate_limit(request, max_requests: int = 60, window: int = 60):
    """
    检查IP请求频率限制
    :param request: FastAPI请求对象
    :param max_requests: 指定时间窗口内的最大请求数
    :param window: 时间窗口（秒）
    :return: True if within limit, otherwise raises HTTPException
    """
    client_ip = request.client.host
    
    # 获取当前时间
    current_time = time.time()
    
    # 清理窗口外的请求记录
    ip_requests[client_ip] = [
        req_time for req_time in ip_requests[client_ip] 
        if current_time - req_time < window
    ]
    
    # 检查是否超过限制
    if len(ip_requests[client_ip]) >= max_requests:
        raise HTTPException(
            status_code=429,
            detail=f"请求频率超限，IP {client_ip} 在 {window} 秒内已达到 {max_requests} 次请求限制"
        )
    
    # 记录当前请求
    ip_requests[client_ip].append(current_time)
    
    return True