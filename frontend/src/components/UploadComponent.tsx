import React, { useState, useRef, DragEvent, ChangeEvent } from 'react';
import ImagePreview from './ImagePreview';
import apiClient from '../services/api';

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
  const [uploadStatus, setUploadStatus] = useState<'idle' | 'valid' | 'invalid' | 'uploading' | 'success' | 'error'>('idle');
  const [progress, setProgress] = useState<number>(0);
  const [errorMessages, setErrorMessages] = useState<string[]>([]);
  const [taskId, setTaskId] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // 允许的文件类型
  const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp', 'image/bmp'];
  const maxSize = 10 * 1024 * 1024; // 10MB

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
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) return;

    setUploadStatus('uploading');
    setProgress(0);
    setErrorMessages([]);

    try {
      const response = await apiClient.uploadImage(selectedFile, (progress: number) => {
        setProgress(Math.round(progress));
      });
      
      setUploadStatus('success');
      setTaskId(response.upload_id || response.task_id);
      
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
          {previewUrl && selectedFile ? (
            <ImagePreview 
              src={previewUrl}
              fileName={selectedFile.name}
              fileSize={selectedFile.size}
              fileType={selectedFile.type}
              onRemove={handleRemoveFile}
            />
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
          
          {selectedFile && (
            <div className="upload-controls">
              {uploadStatus === 'uploading' ? (
                <div className="progress-container">
                  <div className="progress-bar">
                    <div 
                      className="progress-fill" 
                      style={{ width: `${progress}%` }}
                    ></div>
                  </div>
                  <div className="progress-text">{progress}%</div>
                </div>
              ) : null}
              
              <button 
                onClick={handleUpload} 
                className="upload-btn"
                disabled={uploadStatus === 'uploading' || uploadStatus === 'success'}
              >
                {uploadStatus === 'uploading' ? '上传中...' : '开始上传'}
              </button>
            </div>
          )}
          
          {uploadStatus === 'success' && taskId && (
            <div className="success-message">
              <p>上传成功！任务ID: {taskId}</p>
            </div>
          )}
          
          {uploadStatus === 'error' && errorMessages.length > 0 && (
            <div className="error-messages">
              {errorMessages.map((error, index) => (
                <p key={index} className="error-message">{error}</p>
              ))}
              <button onClick={handleUpload} className="retry-btn">重试</button>
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