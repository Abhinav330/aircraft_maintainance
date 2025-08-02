import React, { useCallback, useState, useRef } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, Image, AlertCircle, CheckCircle } from 'lucide-react';
import { useMaintenanceLog } from '../context/MaintenanceLogContext';

const UploadArea = () => {
  const { uploadLog, uploading } = useMaintenanceLog();
  const [uploadedFile, setUploadedFile] = useState(null);
  const [error, setError] = useState(null);
  const fileInputRef = useRef(null);

  const onDrop = useCallback(async (acceptedFiles, rejectedFiles) => {
    setError(null);
    
    if (rejectedFiles.length > 0) {
      setError('Please upload a valid image file (JPEG, PNG, WebP, TIFF)');
      return;
    }

    if (acceptedFiles.length > 0) {
      const file = acceptedFiles[0];
      setUploadedFile(file);
      
      try {
        await uploadLog(file);
        setUploadedFile(null); // Clear after successful upload
      } catch (err) {
        setError('Failed to upload and analyze the image. Please try again.');
        setUploadedFile(null);
      }
    }
  }, [uploadLog]);

  const { getRootProps, getInputProps, isDragActive, isDragReject } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.jpeg', '.jpg', '.png', '.webp', '.tiff', '.tif']
    },
    maxFiles: 1,
    disabled: uploading
  });

  const handleChooseFileClick = (e) => {
    e.stopPropagation();
    if (fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  const getUploadText = () => {
    if (uploading) {
      return 'Processing...';
    }
    if (isDragActive) {
      return 'Drop the maintenance log image here';
    }
    if (isDragReject) {
      return 'Invalid file type';
    }
    return 'Drag & drop a maintenance log image, or click to select';
  };

  const getUploadIcon = () => {
    if (uploading) {
      return <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-aviation-600"></div>;
    }
    if (isDragActive && !isDragReject) {
      return <CheckCircle className="w-8 h-8 text-green-600" />;
    }
    if (isDragReject) {
      return <AlertCircle className="w-8 h-8 text-red-600" />;
    }
    return <Upload className="w-8 h-8 text-aviation-600" />;
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Upload Area */}
        <div
          {...getRootProps()}
          className={`border-2 border-dashed rounded-lg p-6 text-center transition-all duration-200 cursor-pointer ${
            isDragActive && !isDragReject
              ? 'border-green-400 bg-green-50'
              : isDragReject
              ? 'border-red-400 bg-red-50'
              : 'border-gray-300 bg-gray-50 hover:border-aviation-400 hover:bg-aviation-50'
          } ${uploading ? 'opacity-50 cursor-not-allowed' : ''}`}
        >
          <input {...getInputProps()} ref={fileInputRef} />
          
          <div className="flex flex-col items-center space-y-3">
            {getUploadIcon()}
            
            <div>
              <p className="text-base font-medium text-gray-900 mb-1">
                {getUploadText()}
              </p>
              <p className="text-xs text-gray-500">
                Supports JPEG, PNG, WebP, and TIFF formats
              </p>
            </div>

            {!uploading && (
              <button
                type="button"
                className="btn-primary"
                onClick={handleChooseFileClick}
              >
                Choose File
              </button>
            )}
          </div>
        </div>

        {/* Instructions */}
        <div className="card">
          <h3 className="font-semibold text-gray-900 mb-3 text-sm">Upload Instructions</h3>
          <ul className="text-xs text-gray-600 space-y-2">
            <li className="flex items-start space-x-2">
              <span className="w-1.5 h-1.5 bg-aviation-600 rounded-full mt-1.5 flex-shrink-0"></span>
              <span>Ensure the maintenance log is clearly visible and well-lit</span>
            </li>
            <li className="flex items-start space-x-2">
              <span className="w-1.5 h-1.5 bg-aviation-600 rounded-full mt-1.5 flex-shrink-0"></span>
              <span>Include all relevant sections: aircraft info, work performed, technician details</span>
            </li>
            <li className="flex items-start space-x-2">
              <span className="w-1.5 h-1.5 bg-aviation-600 rounded-full mt-1.5 flex-shrink-0"></span>
              <span>Both handwritten and printed logs are supported</span>
            </li>
            <li className="flex items-start space-x-2">
              <span className="w-1.5 h-1.5 bg-aviation-600 rounded-full mt-1.5 flex-shrink-0"></span>
              <span>Maximum file size: 10MB</span>
            </li>
          </ul>
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
          <div className="flex items-center space-x-2">
            <AlertCircle className="w-5 h-5 text-red-600" />
            <p className="text-red-700">{error}</p>
          </div>
        </div>
      )}

      {/* Uploaded File Preview */}
      {uploadedFile && (
        <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <div className="flex items-center space-x-3">
            <Image className="w-5 h-5 text-blue-600" />
            <div className="flex-1">
              <p className="text-sm font-medium text-blue-900">
                {uploadedFile.name}
              </p>
              <p className="text-xs text-blue-700">
                {(uploadedFile.size / 1024 / 1024).toFixed(2)} MB
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default UploadArea; 