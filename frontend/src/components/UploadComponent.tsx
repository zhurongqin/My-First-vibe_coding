import React, { useState, useRef, DragEvent, ChangeEvent, useEffect } from 'react';
import ImagePreview from './ImagePreview';
import apiClient from '../services/api';
import { API_BASE_URL } from '../config/api';

interface FileUploadProps {
  onFileUpload?: (file: File) => void;
  onUploadSuccess?: (response: any) => void;
  onUploadError?: (error: any) => void;
}

const UploadComponent: React.FC<FileUploadProps> = ({ 
  onFileUpload, 
  onUploadSuccess, 
  onUploadError 
}) => {
  const [dragActive, setDragActive] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [uploadStatus, setUploadStatus] = useState<'idle' | 'valid' | 'invalid' | 'uploading' | 'processing' | 'success' | 'error'>('idle');
  const [progress, setProgress] = useState<number>(0);
  const [errorMessages, setErrorMessages] = useState<string[]>([]);
  const [taskId, setTaskId] = useState<string | null>(null);
  const [processedImageUrl, setProcessedImageUrl] = useState<string | null>(null);
  const [taskStatusMessage, setTaskStatusMessage] = useState<string>('');
  const fileInputRef = useRef<HTMLInputElement>(null);
  const pollingRef = useRef<NodeJS.Timeout | null>(null);
  const retryCountRef = useRef<number>(0);
  const maxRetries = 3;

  // 允许的文件类型
  const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp', 'image/bmp'];
  const maxSize = 10 * 1024 * 1024; // 10MB

  // 清理轮询定时器
  useEffect(() => {
    return () => {
      if (pollingRef.current) {
        clearInterval(pollingRef.current);
      }
    };
  }, []);

  const validateFile = (file: File): boolean => {
    const errors: string[] = [];
    
    if (!allowedTypes.includes(file.type)) {
      errors.push(`不支持的文件类型: ${file.type}`);
    }

    if (file.size > maxSize) {
      errors.push(`文件大小超出限制: ${(file.size / 1024 / 1024).toFixed(2)}MB (最大10MB)`);
    }

    setErrorMessages(errors);
    setUploadStatus(errors.length === 0 ? 'valid' : 'invalid');
    
    return errors.length === 0;
  };

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      processFile(file);
    }
  };

  const processFile = (file: File) => {
    if (validateFile(file)) {
      setSelectedFile(file);
      
      // 创建预览URL
      const url = URL.createObjectURL(file);
      setPreviewUrl(url);
      
      // 通知父组件文件已选择
      if (onFileUpload) {
        onFileUpload(file);
      }
    }
  };

  const handleDrag = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      processFile(file);
    }
  };

  const handleButtonClick = () => {
    if (fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  const handleRemoveFile = () => {
    setSelectedFile(null);
    setPreviewUrl(null);
    setUploadStatus('idle');
    setErrorMessages([]);
    setProgress(0);
    setTaskId(null);
    setProcessedImageUrl(null);
    setTaskStatusMessage('');
    retryCountRef.current = 0;
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
    
    // 清除轮询
    if (pollingRef.current) {
      clearInterval(pollingRef.current);
      pollingRef.current = null;
    }
  };

  // 开始轮询任务状态
  const startPolling = (id: string) => {
    if (pollingRef.current) {
      clearInterval(pollingRef.current);
    }
    
    setUploadStatus('processing');
    setTaskStatusMessage('任务正在排队中...');
    
    pollingRef.current = setInterval(async () => {
      try {
        const status = await apiClient.getProcessingStatus(id);
        
        switch (status.status) {
          case 'pending':
            setTaskStatusMessage('任务正在排队中...');
            setProgress(10);
            break;
          case 'processing':
            setTaskStatusMessage(status.message || '图像处理中...');
            setProgress(status.progress || 50);
            break;
          case 'completed':
            setTaskStatusMessage('处理完成！');
            setProgress(100);
            if (pollingRef.current) {
              clearInterval(pollingRef.current);
              pollingRef.current = null;
            }
            setUploadStatus('success');
            setProcessedImageUrl(`${API_BASE_URL}/api/v1/tasks/download/${id}`);
            retryCountRef.current = 0; // 重置重试计数
            break;
          case 'failed':
            setTaskStatusMessage('处理失败');
            setUploadStatus('error');
            setErrorMessages([status.message || '任务处理失败']);
            if (pollingRef.current) {
              clearInterval(pollingRef.current);
              pollingRef.current = null;
            }
            break;
          default:
            setTaskStatusMessage('未知状态');
        }
      } catch (error: any) {
        console.error('获取任务状态失败:', error);
        if (pollingRef.current) {
          clearInterval(pollingRef.current);
          pollingRef.current = null;
        }
        setUploadStatus('error');
        setErrorMessages(['获取任务状态失败']);
        if (onUploadError) {
          onUploadError(error);
        }
      }
    }, 2000); // 每2秒轮询一次
  };

  const handleRetry = async () => {
    if (retryCountRef.current >= maxRetries) {
      setErrorMessages([`已达到最大重试次数 (${maxRetries}次)`]);
      return;
    }

    retryCountRef.current += 1;
    setUploadStatus('uploading');
    setErrorMessages([]);
    
    if (!selectedFile) return;

    try {
      const response = await apiClient.uploadImage(selectedFile, (progress: number) => {
        setProgress(Math.round(progress));
      });
      
      const id = response.task_id;
      setTaskId(id);
      
      // 开始轮询任务状态
      startPolling(id);
      
      if (onUploadSuccess) {
        onUploadSuccess(response);
      }
    } catch (error: any) {
      setUploadStatus('error');
      const errorMsg = error.message || `上传失败，请重试 (${retryCountRef.current}/${maxRetries})`;
      setErrorMessages([errorMsg]);
      
      if (retryCountRef.current >= maxRetries) {
        setErrorMessages([`${errorMsg}，已达到最大重试次数`]);
      }
      
      if (onUploadError) {
        onUploadError(error);
      }
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) return;

    setUploadStatus('uploading');
    setProgress(0);
    setErrorMessages([]);
    retryCountRef.current = 0; // 重置重试计数

    try {
      const response = await apiClient.uploadImage(selectedFile, (progress: number) => {
        setProgress(Math.round(progress));
      });
      
      const id = response.task_id;
      setTaskId(id);
      
      // 开始轮询任务状态
      startPolling(id);
      
      if (onUploadSuccess) {
        onUploadSuccess(response);
      }
    } catch (error: any) {
      setUploadStatus('error');
      setErrorMessages([error.message || '上传失败，请重试']);
      
      if (onUploadError) {
        onUploadError(error);
      }
    }
  };

  return (
    <div className="upload-container">
      <div
        className={`upload-area ${dragActive ? 'drag-active' : ''} ${
          uploadStatus === 'valid' || uploadStatus === 'success' ? 'valid-upload' : 
          uploadStatus === 'invalid' || uploadStatus === 'error' ? 'invalid-upload' : 
          ''
        }`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <div className="upload-content">
          {previewUrl && selectedFile && !processedImageUrl ? (
            <ImagePreview 
              src={previewUrl}
              fileName={selectedFile.name}
              fileSize={selectedFile.size}
              fileType={selectedFile.type}
              onRemove={handleRemoveFile}
            />
          ) : processedImageUrl ? (
            <div className="result-container">
              <h3>处理结果</h3>
              <img 
                src={processedImageUrl} 
                alt="处理后的图像" 
                style={{ maxWidth: '100%', maxHeight: '400px', objectFit: 'contain' }}
              />
              <div className="result-actions">
                <a 
                  href={processedImageUrl} 
                  download={`processed_${selectedFile?.name || 'image'}`}
                  className="download-btn"
                >
                  下载图像
                </a>
                <button onClick={handleRemoveFile} className="new-upload-btn">
                  上传新图像
                </button>
              </div>
            </div>
          ) : (
            <>
              <p>拖拽文件到此处或点击上传</p>
              <p className="file-hint">
                支持格式: JPG, PNG, WEBP, BMP (最大10MB)
              </p>
              <button 
                onClick={handleButtonClick} 
                className="upload-btn"
              >
                选择文件
              </button>
              {uploadStatus === 'invalid' && errorMessages.length > 0 && (
                <div className="error-messages">
                  {errorMessages.map((error, index) => (
                    <p key={index} className="error-message">{error}</p>
                  ))}
                </div>
              )}
            </>
          )}
          
          {selectedFile && !processedImageUrl && (
            <div className="upload-controls">
              {uploadStatus === 'uploading' || uploadStatus === 'processing' ? (
                <div className="progress-container">
                  <div className="progress-bar">
                    <div 
                      className="progress-fill" 
                      style={{ width: `${progress}%` }}
                    ></div>
                  </div>
                  <div className="progress-text">{progress}% {taskStatusMessage && `- ${taskStatusMessage}`}</div>
                </div>
              ) : null}
              
              <button 
                onClick={handleUpload} 
                className="upload-btn"
                disabled={uploadStatus === 'uploading' || uploadStatus === 'processing' || uploadStatus === 'success'}
              >
                {uploadStatus === 'uploading' ? '上传中...' : 
                 uploadStatus === 'processing' ? '处理中...' : 
                 '开始上传'}
              </button>
            </div>
          )}
          
          {uploadStatus === 'success' && taskId && !processedImageUrl && (
            <div className="success-message">
              <p>上传成功！任务ID: {taskId}</p>
            </div>
          )}
          
          {uploadStatus === 'error' && errorMessages.length > 0 && (
            <div className="error-messages">
              {errorMessages.map((error, index) => (
                <p key={index} className="error-message">{error}</p>
              ))}
              <div className="error-actions">
                <button onClick={handleRetry} className="retry-btn">重试</button>
                <span className="retry-count">({retryCountRef.current}/{maxRetries})</span>
              </div>
            </div>
          )}
        </div>
        
        <input
          ref={fileInputRef}
          type="file"
          className="file-input"
          onChange={handleFileChange}
          accept={allowedTypes.join(',')}
        />
      </div>
    </div>
  );
};

export default UploadComponent;