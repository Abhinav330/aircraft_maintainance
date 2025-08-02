import React, { useState } from 'react';
import { 
  Edit3, 
  Save, 
  X, 
  Download, 
  FileText, 
  Plane, 
  Clock, 
  User,
  AlertTriangle,
  CheckCircle,
  Calendar,
  Hash,
  Plus,
  ZoomIn,
  ZoomOut,
  RotateCcw,
  ChevronDown,
  ChevronRight
} from 'lucide-react';
import { useMaintenanceLog } from '../context/MaintenanceLogContext';
import { format } from 'date-fns';

const LogDisplay = ({ log }) => {
  const { updateLog, exportLog, clearCurrentLog } = useMaintenanceLog();
  const [isEditing, setIsEditing] = useState(false);
  const [editedData, setEditedData] = useState(log.structured_data);
  const [zoomLevel, setZoomLevel] = useState(1);
  const [expandedEntries, setExpandedEntries] = useState(new Set());
  const [panPosition, setPanPosition] = useState({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });

  const handleZoomIn = () => {
    setZoomLevel(prev => Math.min(prev + 0.25, 3));
  };

  const handleZoomOut = () => {
    setZoomLevel(prev => Math.max(prev - 0.25, 0.5));
  };

  const handleResetZoom = () => {
    setZoomLevel(1);
    setPanPosition({ x: 0, y: 0 });
  };

  const handleMouseDown = (e) => {
    if (zoomLevel > 1) {
      setIsDragging(true);
      setDragStart({
        x: e.clientX - panPosition.x,
        y: e.clientY - panPosition.y
      });
    }
  };

  const handleMouseMove = (e) => {
    if (isDragging && zoomLevel > 1) {
      setPanPosition({
        x: e.clientX - dragStart.x,
        y: e.clientY - dragStart.y
      });
    }
  };

  const handleMouseUp = () => {
    setIsDragging(false);
  };

  const handleMouseLeave = () => {
    setIsDragging(false);
  };

  const handleEdit = () => {
    setIsEditing(true);
    setEditedData(log.structured_data);
  };

  const handleCancel = () => {
    setIsEditing(false);
    setEditedData(log.structured_data);
  };

  const handleSave = async () => {
    try {
      await updateLog(log._id, editedData);
      setIsEditing(false);
    } catch (error) {
      console.error('Error updating log:', error);
    }
  };

  const handleFieldChange = (field, value) => {
    setEditedData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleEntryFieldChange = (entryIndex, field, value) => {
    setEditedData(prev => ({
      ...prev,
      log_entries: prev.log_entries.map((entry, index) => 
        index === entryIndex 
          ? { ...entry, [field]: value }
          : entry
      )
    }));
  };

  const handleArrayFieldChange = (entryIndex, field, itemIndex, value) => {
    setEditedData(prev => ({
      ...prev,
      log_entries: prev.log_entries.map((entry, index) => 
        index === entryIndex 
          ? {
              ...entry,
              [field]: entry[field].map((item, i) => i === itemIndex ? value : item)
            }
          : entry
      )
    }));
  };

  const addArrayItem = (entryIndex, field) => {
    setEditedData(prev => ({
      ...prev,
      log_entries: prev.log_entries.map((entry, index) => 
        index === entryIndex 
          ? { ...entry, [field]: [...entry[field], ''] }
          : entry
      )
    }));
  };

  const removeArrayItem = (entryIndex, field, itemIndex) => {
    setEditedData(prev => ({
      ...prev,
      log_entries: prev.log_entries.map((entry, index) => 
        index === entryIndex 
          ? { ...entry, [field]: entry[field].filter((_, i) => i !== itemIndex) }
          : entry
      )
    }));
  };

  const toggleEntryExpansion = (entryIndex) => {
    setExpandedEntries(prev => {
      const newSet = new Set(prev);
      if (newSet.has(entryIndex)) {
        newSet.delete(entryIndex);
      } else {
        newSet.add(entryIndex);
      }
      return newSet;
    });
  };

  const getRiskColor = (riskLevel) => {
    switch (riskLevel?.toLowerCase()) {
      case 'high':
        return 'text-red-600 bg-red-100';
      case 'medium':
        return 'text-yellow-600 bg-yellow-100';
      case 'low':
        return 'text-green-600 bg-green-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  const getUrgencyColor = (urgency) => {
    switch (urgency?.toLowerCase()) {
      case 'high':
        return 'text-red-600 bg-red-100';
      case 'medium':
        return 'text-yellow-600 bg-yellow-100';
      case 'normal':
        return 'text-green-600 bg-green-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  const renderField = (label, field, type = 'text', options = null) => {
    const value = editedData[field];
    
    if (isEditing) {
      switch (type) {
        case 'textarea':
          return (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {label}
              </label>
              <textarea
                value={value || ''}
                onChange={(e) => handleFieldChange(field, e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                rows={3}
              />
            </div>
          );
        case 'select':
          return (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {label}
              </label>
              <select
                value={value || ''}
                onChange={(e) => handleFieldChange(field, e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Select...</option>
                {options?.map(option => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>
          );
        case 'checkbox':
          return (
            <div className="flex items-center">
              <input
                type="checkbox"
                checked={value || false}
                onChange={(e) => handleFieldChange(field, e.target.checked)}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <label className="ml-2 block text-sm text-gray-900">
                {label}
              </label>
            </div>
          );
        default:
          return (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {label}
              </label>
              <input
                type={type}
                value={value || ''}
                onChange={(e) => handleFieldChange(field, e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          );
      }
    } else {
      return (
        <div>
          <p className="text-sm font-medium text-gray-500">{label}</p>
          <p className="text-gray-900">
            {type === 'checkbox' 
              ? (value ? 'Yes' : 'No')
              : value || 'Not specified'
            }
          </p>
        </div>
      );
    }
  };

  const renderEntryField = (entryIndex, label, field, type = 'text', options = null) => {
    const entry = editedData.log_entries[entryIndex];
    const value = entry[field];
    
    if (isEditing) {
      switch (type) {
        case 'textarea':
          return (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {label}
              </label>
              <textarea
                value={value || ''}
                onChange={(e) => handleEntryFieldChange(entryIndex, field, e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                rows={3}
              />
            </div>
          );
        case 'select':
          return (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {label}
              </label>
              <select
                value={value || ''}
                onChange={(e) => handleEntryFieldChange(entryIndex, field, e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Select...</option>
                {options?.map(option => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>
          );
        case 'checkbox':
          return (
            <div className="flex items-center">
              <input
                type="checkbox"
                checked={value || false}
                onChange={(e) => handleEntryFieldChange(entryIndex, field, e.target.checked)}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <label className="ml-2 block text-sm text-gray-900">
                {label}
              </label>
            </div>
          );
        default:
          return (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {label}
              </label>
              <input
                type={type}
                value={value || ''}
                onChange={(e) => handleEntryFieldChange(entryIndex, field, e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          );
      }
    } else {
      return (
        <div>
          <p className="text-sm font-medium text-gray-500">{label}</p>
          <p className="text-gray-900">
            {type === 'checkbox' 
              ? (value ? 'Yes' : 'No')
              : value || 'Not specified'
            }
          </p>
        </div>
      );
    }
  };

  const renderArrayField = (entryIndex, label, field) => {
    const entry = editedData.log_entries[entryIndex];
    const value = entry[field] || [];
    
    if (isEditing) {
      return (
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            {label}
          </label>
          <div className="space-y-2">
            {value.map((item, index) => (
              <div key={index} className="flex space-x-2">
                <input
                  type="text"
                  value={item}
                  onChange={(e) => handleArrayFieldChange(entryIndex, field, index, e.target.value)}
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <button
                  onClick={() => removeArrayItem(entryIndex, field, index)}
                  className="px-3 py-2 text-red-600 hover:text-red-800"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            ))}
            <button
              onClick={() => addArrayItem(entryIndex, field)}
              className="text-blue-600 hover:text-blue-800 text-sm"
            >
              + Add {label.toLowerCase()}
            </button>
          </div>
        </div>
      );
    } else {
      return (
        <div>
          <p className="text-sm font-medium text-gray-500">{label}</p>
          {value?.length > 0 ? (
            <div className="space-y-1">
              {value.map((item, index) => (
                <p key={index} className="text-gray-900">
                  • {item}
                </p>
              ))}
            </div>
          ) : (
            <p className="text-gray-500">None specified</p>
          )}
        </div>
      );
    }
  };

  const renderLogEntry = (entry, index) => {
    const isExpanded = expandedEntries.has(index);
    
    return (
      <div key={index} className="card">
        <div 
          className="flex items-center justify-between cursor-pointer"
          onClick={() => toggleEntryExpansion(index)}
        >
          <div className="flex items-center space-x-3">
            <div className="p-2 rounded-full bg-blue-100">
              <FileText className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <h4 className="text-lg font-semibold text-gray-900">
                Entry #{index + 1}
              </h4>
              <p className="text-sm text-gray-500">
                {entry.description_of_work_performed || 'No description'}
              </p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <span className="text-sm text-gray-500">
              {entry.date || 'No date'}
            </span>
            {isExpanded ? (
              <ChevronDown className="w-5 h-5 text-gray-400" />
            ) : (
              <ChevronRight className="w-5 h-5 text-gray-400" />
            )}
          </div>
        </div>
        
        {isExpanded && (
          <div className="mt-4 pt-4 border-t border-gray-200">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 relative">
              {/* Left Column */}
              <div className="space-y-3">
                {/* Work Information */}
                <div>
                  <h5 className="text-sm font-semibold text-gray-900 mb-2">Work Information</h5>
                  <div className="space-y-2">
                    {renderEntryField(index, 'Description of Work Performed', 'description_of_work_performed', 'textarea')}
                    {renderEntryField(index, 'Reason for Maintenance', 'reason_for_maintenance')}
                    {renderArrayField(index, 'Part Numbers Replaced', 'part_number_replaced')}
                    {renderEntryField(index, 'Manual Reference', 'manual_reference')}
                  </div>
                </div>

                {/* Compliance Information */}
                <div>
                  <h5 className="text-sm font-semibold text-gray-900 mb-2">Compliance Information</h5>
                  <div className="space-y-2">
                    {renderEntryField(index, 'AD Compliance', 'ad_compliance')}
                    {renderEntryField(index, 'Next Due Compliance', 'next_due_compliance')}
                    {renderEntryField(index, 'Service Bulletin Reference', 'service_bulletin_reference')}
                  </div>
                </div>
              </div>

              {/* Vertical divider line */}
              <div className="hidden lg:block absolute left-1/2 top-0 bottom-0 w-px bg-gray-200 transform -translate-x-1/2"></div>

              {/* Right Column */}
              <div className="space-y-3">
                {/* Technician Information */}
                <div>
                  <h5 className="text-sm font-semibold text-gray-900 mb-2">Technician Information</h5>
                  <div className="space-y-2">
                    {renderEntryField(index, 'Performed By', 'performed_by')}
                    {renderEntryField(index, 'License Number', 'license_number')}
                    {renderEntryField(index, 'Date', 'date')}
                    {renderEntryField(index, 'Tach Time', 'tach_time')}
                    {renderEntryField(index, 'Hobbs Time', 'hobbs_time')}
                  </div>
                </div>

                {/* Risk Assessment */}
                <div>
                  <h5 className="text-sm font-semibold text-gray-900 mb-2">Risk Assessment</h5>
                  <div className="space-y-2">
                    {renderEntryField(index, 'Risk Level', 'risk_level', 'select', [
                      { value: 'Low', label: 'Low' },
                      { value: 'Medium', label: 'Medium' },
                      { value: 'High', label: 'High' }
                    ])}
                    {renderEntryField(index, 'Urgency', 'urgency', 'select', [
                      { value: 'Normal', label: 'Normal' },
                      { value: 'Medium', label: 'Medium' },
                      { value: 'High', label: 'High' }
                    ])}
                    {renderEntryField(index, 'Is Airworthy', 'is_airworthy', 'checkbox')}
                  </div>
                </div>

                {/* Certification */}
                <div>
                  <h5 className="text-sm font-semibold text-gray-900 mb-2">Certification</h5>
                  <div className="space-y-2">
                    {renderEntryField(index, 'Certification Statement', 'certification_statement', 'textarea')}
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    );
  };

  const getHighestRiskLevel = () => {
    const riskLevels = editedData.log_entries.map(entry => entry.risk_level);
    if (riskLevels.length === 0) return 'Unknown';
    const uniqueLevels = [...new Set(riskLevels)];
    if (uniqueLevels.length === 1) return uniqueLevels[0];
    return 'Mixed';
  };

  const getHighestUrgency = () => {
    const urgencies = editedData.log_entries.map(entry => entry.urgency);
    if (urgencies.length === 0) return 'Unknown';
    const uniqueLevels = [...new Set(urgencies)];
    if (uniqueLevels.length === 1) return uniqueLevels[0];
    return 'Mixed';
  };

  const getOverallAirworthiness = () => {
    return editedData.log_entries.every(entry => entry.is_airworthy);
  };

  const getOverallAirworthinessColor = () => {
    return getOverallAirworthiness() ? 'text-green-600 bg-green-100' : 'text-red-600 bg-red-100';
  };

  return (
    <div className="max-w-6xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div>
          <h2 className="text-xl font-bold text-gray-900">
            Maintenance Log Analysis
          </h2>
          <p className="text-sm text-gray-500">
            {log.aircraft_registration && `Aircraft: ${log.aircraft_registration}`} • 
            {format(new Date(log.timestamp), 'MMM d, yyyy HH:mm')}
          </p>
        </div>
        
        <div className="flex space-x-2">
          {isEditing ? (
            <>
              <button onClick={handleSave} className="btn-primary">
                <Save className="w-4 h-4 mr-2" />
                Save
              </button>
              <button onClick={handleCancel} className="btn-secondary">
                <X className="w-4 h-4 mr-2" />
                Cancel
              </button>
            </>
          ) : (
            <>
              <button onClick={handleEdit} className="btn-secondary">
                <Edit3 className="w-4 h-4 mr-2" />
                Edit
              </button>
              <button 
                onClick={() => exportLog(log._id, 'pdf')} 
                className="btn-primary"
              >
                <Download className="w-4 h-4 mr-2" />
                Export PDF
              </button>
              <button 
                onClick={clearCurrentLog} 
                className="btn-primary"
              >
                <Plus className="w-4 h-4 mr-2" />
                New Log
              </button>
            </>
          )}
        </div>
      </div>

              {/* Original Image Display */}
        {log.image_filename && (
          <div className="mb-4">
          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900 flex items-center">
                <FileText className="w-5 h-5 mr-2" />
                Original Maintenance Log Image
                {zoomLevel > 1 && (
                  <span className="ml-2 text-sm text-blue-600 font-normal">
                    (Drag to pan)
                  </span>
                )}
              </h3>
              <div className="flex items-center space-x-2">
                <button
                  onClick={handleZoomOut}
                  disabled={zoomLevel <= 0.5}
                  className="p-2 rounded-md hover:bg-gray-100 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  title="Zoom Out"
                >
                  <ZoomOut className="w-4 h-4" />
                </button>
                <span className="text-sm text-gray-600 min-w-[60px] text-center">
                  {Math.round(zoomLevel * 100)}%
                </span>
                <button
                  onClick={handleZoomIn}
                  disabled={zoomLevel >= 3}
                  className="p-2 rounded-md hover:bg-gray-100 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  title="Zoom In"
                >
                  <ZoomIn className="w-4 h-4" />
                </button>
                <button
                  onClick={handleResetZoom}
                  className="p-2 rounded-md hover:bg-gray-100 transition-colors"
                  title="Reset Zoom"
                >
                  <RotateCcw className="w-4 h-4" />
                </button>
              </div>
            </div>
            <div className="bg-gray-50 rounded-lg p-4 border-2 border-dashed border-gray-200">
              <div className="text-center overflow-hidden">
                <img 
                  src={`http://localhost:8000/api/v1/images/${encodeURIComponent(log.image_filename)}`}
                  alt="Original maintenance log"
                  className="rounded-lg shadow-md transition-transform duration-200 max-w-full h-auto max-h-96 mx-auto"
                  style={{
                    transform: `scale(${zoomLevel}) translate(${panPosition.x}px, ${panPosition.y}px)`,
                    transformOrigin: 'center',
                    cursor: zoomLevel > 1 ? (isDragging ? 'grabbing' : 'grab') : 'default',
                  }}
                  onError={(e) => {
                    console.error('Image failed to load:', e.target.src);
                    e.target.style.display = 'none';
                    e.target.nextSibling.style.display = 'block';
                  }}
                  onLoad={(e) => {
                    console.log('Image loaded successfully:', e.target.src);
                  }}
                  onMouseDown={handleMouseDown}
                  onMouseMove={handleMouseMove}
                  onMouseUp={handleMouseUp}
                  onMouseLeave={handleMouseLeave}
                />
                <div className="hidden text-center mt-4">
                  <FileText className="w-12 h-12 text-gray-400 mx-auto mb-2" />
                  <p className="text-sm text-gray-500 mb-2">
                    Original image: {log.image_filename}
                  </p>
                  <p className="text-xs text-gray-400">
                    Image analysis completed successfully
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Status Indicators */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mb-4">
        <div className="card">
          <div className="flex items-center space-x-3">
            <div className={`p-2 rounded-full ${getRiskColor(getHighestRiskLevel())}`}>
              <AlertTriangle className="w-5 h-5" />
            </div>
            <div>
              <p className="text-sm font-medium text-gray-500">Overall Risk Level</p>
              <p className="text-lg font-semibold text-gray-900">
                {getHighestRiskLevel() || 'Unknown'}
              </p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center space-x-3">
            <div className={`p-2 rounded-full ${getUrgencyColor(getHighestUrgency())}`}>
              <Clock className="w-5 h-5" />
            </div>
            <div>
              <p className="text-sm font-medium text-gray-500">Highest Urgency</p>
              <p className="text-lg font-semibold text-gray-900">
                {getHighestUrgency() || 'Unknown'}
              </p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center space-x-3">
            <div className={`p-2 rounded-full ${getOverallAirworthinessColor()}`}>
              {getOverallAirworthiness() ? <CheckCircle className="w-5 h-5" /> : <AlertTriangle className="w-5 h-5" />}
            </div>
            <div>
              <p className="text-sm font-medium text-gray-500">Overall Airworthiness</p>
              <p className="text-lg font-semibold text-gray-900">
                {getOverallAirworthiness() ? 'Airworthy' : 'Not Airworthy'}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="space-y-4">
        {/* Aircraft Information */}
        <div className="card">
          <h3 className="text-md font-semibold text-gray-900 mb-3 flex items-center">
            <Plane className="w-4 h-4 mr-2" />
            Aircraft Information
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {renderField('Aircraft Registration', 'aircraft_registration')}
            {renderField('Aircraft Make/Model', 'aircraft_make_model')}
          </div>
        </div>



        {/* Summary Section - Show if summary exists and multiple entries */}
        {editedData.summary && editedData.log_entries?.length > 1 && (
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <FileText className="w-5 h-5 mr-2" />
              Summary
            </h3>
            <div>
              <p className="text-gray-800 leading-relaxed">
                {isEditing ? (
                  <textarea
                    value={editedData.summary || ''}
                    onChange={(e) => handleFieldChange('summary', e.target.value)}
                    className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                    rows={3}
                    placeholder="Enter summary..."
                  />
                ) : (
                  editedData.summary
                )}
              </p>
            </div>
          </div>
        )}

        {/* Log Entries */}
        {editedData.log_entries?.length === 1 ? (
          // Single entry - show content directly without entry wrapper
          <div className="card">
            <h3 className="text-md font-semibold text-gray-900 mb-3 flex items-center">
              <FileText className="w-4 h-4 mr-2" />
              Maintenance Details
            </h3>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 relative">
              {/* Left Column */}
              <div className="space-y-3">
                {/* Work Information */}
                <div>
                  <h5 className="text-sm font-semibold text-gray-900 mb-2">Work Information</h5>
                  <div className="space-y-2">
                    {renderEntryField(0, 'Description of Work Performed', 'description_of_work_performed', 'textarea')}
                    {renderEntryField(0, 'Reason for Maintenance', 'reason_for_maintenance')}
                    {renderArrayField(0, 'Part Numbers Replaced', 'part_number_replaced')}
                    {renderEntryField(0, 'Manual Reference', 'manual_reference')}
                  </div>
                </div>

                {/* Compliance Information */}
                <div>
                  <h5 className="text-sm font-semibold text-gray-900 mb-2">Compliance Information</h5>
                  <div className="space-y-2">
                    {renderEntryField(0, 'AD Compliance', 'ad_compliance')}
                    {renderEntryField(0, 'Next Due Compliance', 'next_due_compliance')}
                    {renderEntryField(0, 'Service Bulletin Reference', 'service_bulletin_reference')}
                  </div>
                </div>
              </div>

              {/* Vertical divider line */}
              <div className="hidden lg:block absolute left-1/2 top-0 bottom-0 w-px bg-gray-200 transform -translate-x-1/2"></div>

              {/* Right Column */}
              <div className="space-y-3">
                {/* Technician Information */}
                <div>
                  <h5 className="text-sm font-semibold text-gray-900 mb-2">Technician Information</h5>
                  <div className="space-y-2">
                    {renderEntryField(0, 'Performed By', 'performed_by')}
                    {renderEntryField(0, 'License Number', 'license_number')}
                    {renderEntryField(0, 'Date', 'date')}
                    {renderEntryField(0, 'Tach Time', 'tach_time')}
                    {renderEntryField(0, 'Hobbs Time', 'hobbs_time')}
                  </div>
                </div>

                {/* Risk Assessment */}
                <div>
                  <h5 className="text-sm font-semibold text-gray-900 mb-2">Risk Assessment</h5>
                  <div className="space-y-2">
                    {renderEntryField(0, 'Risk Level', 'risk_level', 'select', [
                      { value: 'Low', label: 'Low' },
                      { value: 'Medium', label: 'Medium' },
                      { value: 'High', label: 'High' }
                    ])}
                    {renderEntryField(0, 'Urgency', 'urgency', 'select', [
                      { value: 'Normal', label: 'Normal' },
                      { value: 'Medium', label: 'Medium' },
                      { value: 'High', label: 'High' }
                    ])}
                    {renderEntryField(0, 'Is Airworthy', 'is_airworthy', 'checkbox')}
                  </div>
                </div>

                {/* Certification */}
                <div>
                  <h5 className="text-sm font-semibold text-gray-900 mb-2">Certification</h5>
                  <div className="space-y-2">
                    {renderEntryField(0, 'Certification Statement', 'certification_statement', 'textarea')}
                  </div>
                </div>
              </div>
            </div>
          </div>
        ) : (
          // Multiple entries - show with entry numbers
          <div className="card">
            <h3 className="text-md font-semibold text-gray-900 mb-3 flex items-center">
              <FileText className="w-4 h-4 mr-2" />
              Log Entries ({editedData.log_entries?.length || 0} entries)
            </h3>
            <div className="space-y-4">
              {editedData.log_entries?.map((entry, index) => renderLogEntry(entry, index))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default LogDisplay; 