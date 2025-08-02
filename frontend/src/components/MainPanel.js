import React from 'react';
import { useMaintenanceLog } from '../context/MaintenanceLogContext';
import UploadArea from './UploadArea';
import LogDisplay from './LogDisplay';
import { Plane, Upload } from 'lucide-react';

const MainPanel = () => {
  const { currentLog, loading, uploading, analyzing } = useMaintenanceLog();

  return (
    <div className="flex-1 flex flex-col">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-4 py-3">
        <div className="flex items-center space-x-2">
          <Plane className="w-6 h-6 text-aviation-600" />
          <div>
            <h1 className="text-xl font-bold text-gray-900">
              AI-Powered Aircraft Maintenance Log Analyzer
            </h1>
            <p className="text-xs text-gray-500">
              Upload maintenance log images to extract structured data using AI
            </p>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-auto scrollbar-thin p-4">
        {loading ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-aviation-600 mx-auto mb-4"></div>
              <p className="text-gray-500">Loading maintenance logs...</p>
            </div>
          </div>
        ) : currentLog ? (
          <LogDisplay log={currentLog} />
        ) : (
          <div className="max-w-4xl mx-auto">
            {/* Welcome Section */}
            <div className="text-center mb-6">
              <div className="inline-flex items-center justify-center w-12 h-12 bg-aviation-100 rounded-full mb-3">
                <Upload className="w-6 h-6 text-aviation-600" />
              </div>
              <h2 className="text-lg font-semibold text-gray-900 mb-2">
                Upload Maintenance Log
              </h2>
              <p className="text-sm text-gray-600 max-w-md mx-auto">
                Upload an image of an aircraft maintenance log to extract structured data using AI
              </p>
            </div>

            {/* Upload Area */}
            <UploadArea />

            {/* Features */}
            <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="card text-center">
                <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center mx-auto mb-3">
                  <Plane className="w-5 h-5 text-green-600" />
                </div>
                <h3 className="font-semibold text-gray-900 mb-2 text-sm">AI Analysis</h3>
                <p className="text-xs text-gray-600">
                  Uses GPT-4o Vision to extract structured data from handwritten and printed logs
                </p>
              </div>

              <div className="card text-center">
                <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center mx-auto mb-3">
                  <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                </div>
                <h3 className="font-semibold text-gray-900 mb-2 text-sm">Export & Share</h3>
                <p className="text-xs text-gray-600">
                  Export logs as JSON or PDF for regulatory compliance and sharing
                </p>
              </div>

              <div className="card text-center">
                <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center mx-auto mb-3">
                  <svg className="w-5 h-5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                  </svg>
                </div>
                <h3 className="font-semibold text-gray-900 mb-2 text-sm">Search & Filter</h3>
                <p className="text-xs text-gray-600">
                  Search through maintenance logs by aircraft registration and other criteria
                </p>
              </div>
            </div>

            {/* Supported Formats */}
            <div className="mt-6 card">
              <h3 className="font-semibold text-gray-900 mb-3 text-sm">Supported Image Formats</h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                {['JPEG', 'PNG', 'WebP', 'TIFF'].map((format) => (
                  <div key={format} className="text-center p-2 bg-gray-50 rounded-lg">
                    <span className="text-xs font-medium text-gray-700">{format}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Loading Overlay */}
      {(uploading || analyzing) && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-aviation-600 mx-auto mb-4"></div>
            <p className="text-gray-700 font-medium">
              {analyzing ? 'Analyzing maintenance log with AI...' : 'Uploading image...'}
            </p>
            <p className="text-sm text-gray-500 mt-2">
              This may take a few moments
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

export default MainPanel; 