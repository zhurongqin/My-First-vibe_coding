import React, { useState, useRef, useEffect } from 'react';

interface ImagePreviewProps {
  src: string;
  fileName: string;
  fileSize: number;
  fileType: string;
  onRemove: () => void;
}

const ImagePreview: React.FC<ImagePreviewProps> = ({ 
  src, 
  fileName, 
  fileSize, 
  fileType, 
  onRemove 
}) => {
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(false);
  const [scale, setScale] = useState(1);
  const [position, setPosition] = useState({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });
  const imgRef = useRef<HTMLImageElement>(null);

  useEffect(() => {
    // 重置状态
    setIsLoading(true);
    setError(false);
    setScale(1);
  }, [src]);

  const handleImageLoad = () => {
    setIsLoading(false);
  };

  const handleImageError = () => {
    setError(true);
    setIsLoading(false);
  };

  const handleZoomIn = () => {
    if (scale < 3) {
      setScale(prev => Math.min(prev + 0.2, 3));
    }
  };

  const handleZoomOut = () => {
    if (scale > 0.2) {
      setScale(prev => Math.max(prev - 0.2, 0.2));
    }
  };

  const handleResetZoom = () => {
    setScale(1);
    setPosition({ x: 0, y: 0 });
  };

  const handleMouseDown = (e: React.MouseEvent) => {
    setIsDragging(true);
    setDragStart({
      x: e.clientX - position.x,
      y: e.clientY - position.y
    });
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (isDragging) {
      setPosition({
        x: e.clientX - dragStart.x,
        y: e.clientY - dragStart.y
      });
    }
  };

  const handleMouseUp = () => {
    setIsDragging(false);
  };

  const handleWheel = (e: React.WheelEvent) => {
    e.preventDefault();
    const delta = e.deltaY > 0 ? -0.1 : 0.1;
    const newScale = Math.min(Math.max(0.2, scale + delta), 3);
    setScale(newScale);
  };

  return (
    <div className="preview-container">
      <div className="preview-header">
        <h3>图像预览</h3>
        <button onClick={onRemove} className="remove-btn">移除文件</button>
      </div>
      
      <div className="file-info">
        <p><strong>文件名:</strong> {fileName}</p>
        <p><strong>大小:</strong> {(fileSize / 1024 / 1024).toFixed(2)} MB</p>
        <p><strong>类型:</strong> {fileType}</p>
      </div>
      
      <div className="preview-controls">
        <button onClick={handleZoomIn} disabled={scale >= 3}>放大 (+)</button>
        <button onClick={handleZoomOut} disabled={scale <= 0.2}>缩小 (-)</button>
        <button onClick={handleResetZoom}>重置</button>
        <span>缩放: {Math.round(scale * 100)}%</span>
      </div>
      
      <div 
        className="preview-wrapper" 
        onWheel={handleWheel}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
      >
        {isLoading && <div className="loading">加载中...</div>}
        {error && <div className="error">图像加载失败</div>}
        
        <img
          ref={imgRef}
          src={src}
          alt="预览"
          className={`preview-image ${isLoading ? 'hidden' : ''}`}
          style={{
            transform: `scale(${scale}) translate(${position.x}px, ${position.y}px)`,
            cursor: isDragging ? 'grabbing' : 'grab'
          }}
          onLoad={handleImageLoad}
          onError={handleImageError}
          onMouseDown={handleMouseDown}
        />
      </div>
    </div>
  );
};

export default ImagePreview;