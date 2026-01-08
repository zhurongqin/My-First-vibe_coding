import { API_BASE_URL } from '../config/api';

// API客户端
class ApiClient {
  constructor(baseURL) {
    this.baseURL = baseURL;
  }

  // 健康检查
  async healthCheck() {
    try {
      const response = await fetch(`${this.baseURL}/health`);
      return await response.json();
    } catch (error) {
      console.error('健康检查失败:', error);
      throw error;
    }
  }

  // 上传图片
  async uploadImage(file, onProgress) {
    const formData = new FormData();
    formData.append('file', file);

    return new Promise((resolve, reject) => {
      const xhr = new XMLHttpRequest();

      // 进度处理
      xhr.upload.onprogress = (event) => {
        if (event.lengthComputable && onProgress) {
          const percentComplete = (event.loaded / event.total) * 100;
          onProgress(percentComplete);
        }
      };

      // 成功处理
      xhr.onload = () => {
        if (xhr.status >= 200 && xhr.status < 300) {
          resolve(JSON.parse(xhr.response));
        } else {
          reject(new Error(`上传失败: ${xhr.status}`));
        }
      };

      // 错误处理
      xhr.onerror = () => {
        reject(new Error('网络错误，上传失败'));
      };

      // 连接后端API
      xhr.open('POST', `${this.baseURL}/api/v1/upload/`);
      xhr.send(formData);
    });
  }

  // 获取处理状态
  async getProcessingStatus(taskId) {
    try {
      const response = await fetch(`${this.baseURL}/api/v1/tasks/status/${taskId}`);
      if (!response.ok) {
        throw new Error(`获取状态失败: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error('获取处理状态失败:', error);
      throw error;
    }
  }

  // 获取处理结果
  async getProcessingResult(taskId) {
    try {
      const response = await fetch(`${this.baseURL}/api/v1/tasks/result/${taskId}`);
      if (!response.ok) {
        throw new Error(`获取结果失败: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error('获取处理结果失败:', error);
      throw error;
    }
  }
}

export default new ApiClient(API_BASE_URL);