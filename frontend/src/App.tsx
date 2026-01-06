import React from 'react';
import UploadComponent from './components/UploadComponent';
import './App.css';

function App() {
  const handleFileUpload = (file: File) => {
    console.log('文件已选择:', file.name, file.size, file.type);
  };

  const handleUploadSuccess = (response: any) => {
    console.log('上传成功:', response);
  };

  const handleUploadError = (error: any) => {
    console.error('上传失败:', error);
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>图像背景移除工具</h1>
        <p>上传您的图片，自动移除背景</p>
      </header>
      <main className="main-content">
        <UploadComponent 
          onFileUpload={handleFileUpload}
          onUploadSuccess={handleUploadSuccess}
          onUploadError={handleUploadError}
        />
      </main>
    </div>
  );
}

export default App;