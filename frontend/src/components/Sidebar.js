import React from 'react';
import { 
  ChevronLeft, 
  ChevronRight, 
  Plane, 
  Clock, 
  Search,
  Plus,
  Trash2
} from 'lucide-react';
import { useMaintenanceLog } from '../context/MaintenanceLogContext';
import { format } from 'date-fns';

const Sidebar = ({ isOpen, onToggle }) => {
  const { 
    logs, 
    currentLog, 
    loading, 
    fetchLogById, 
    deleteLog,
    searchLogs 
  } = useMaintenanceLog();

  const [searchTerm, setSearchTerm] = React.useState('');

  const handleLogClick = (logId) => {
    fetchLogById(logId);
  };

  const handleDeleteLog = async (e, logId) => {
    e.stopPropagation();
    
    if (!logId || logId === 'undefined' || logId === undefined) {
      console.error('❌ Invalid log ID for deletion:', logId);
      return;
    }
    
    try {
      await deleteLog(logId);
    } catch (error) {
      console.error('❌ Error in handleDeleteLog:', error);
    }
  };

  const handleSearch = (e) => {
    e.preventDefault();
    if (searchTerm.trim()) {
      searchLogs(searchTerm.trim());
    }
  };

  const getAircraftIcon = (registration) => {
    if (!registration || registration === 'Unknown') {
      return <Plane className="w-4 h-4 text-gray-400" />;
    }
    return <Plane className="w-4 h-4 text-aviation-600" />;
  };

  const getRiskColor = (riskLevel) => {
    switch (riskLevel?.toLowerCase()) {
      case 'high':
        return 'text-red-600';
      case 'medium':
        return 'text-yellow-600';
      case 'low':
        return 'text-green-600';
      default:
        return 'text-gray-400';
    }
  };

  return (
    <div className={`flex flex-col bg-white border-r border-gray-200 transition-all duration-300 ${
      isOpen ? 'w-80' : 'w-16'
    }`}>
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200">
        {isOpen && (
          <div className="flex items-center space-x-2">
            <Plane className="w-6 h-6 text-aviation-600" />
            <h2 className="text-lg font-semibold text-gray-900">
              Maintenance Logs
            </h2>
          </div>
        )}
        <button
          onClick={onToggle}
          className="p-1 rounded-md hover:bg-gray-100 transition-colors"
        >
          {isOpen ? (
            <ChevronLeft className="w-5 h-5 text-gray-500" />
          ) : (
            <ChevronRight className="w-5 h-5 text-gray-500" />
          )}
        </button>
      </div>

      {/* Search */}
      {isOpen && (
        <div className="p-4 border-b border-gray-200">
          <form onSubmit={handleSearch} className="relative">
            <input
              type="text"
              placeholder="Search by aircraft registration..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-aviation-500 focus:border-aviation-500"
            />
            <Search className="absolute left-3 top-2.5 w-4 h-4 text-gray-400" />
          </form>
        </div>
      )}

      {/* Logs List */}
      <div className="flex-1 overflow-y-auto scrollbar-thin">
        {loading ? (
          <div className="flex items-center justify-center p-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-aviation-600"></div>
          </div>
        ) : logs.length === 0 ? (
          <div className="flex flex-col items-center justify-center p-8 text-center">
            <Plane className="w-12 h-12 text-gray-300 mb-4" />
            <p className="text-gray-500 text-sm">
              {isOpen ? 'No maintenance logs yet' : ''}
            </p>
            {isOpen && (
              <p className="text-gray-400 text-xs mt-1">
                Upload a maintenance log to get started
              </p>
            )}
          </div>
        ) : (
          <div className="p-2">
            {logs.map((log) => (
              <div
                key={log._id}
                onClick={(e) => {
                  // Only handle click if the target is not the delete button
                  if (!e.target.closest('button')) {
                    handleLogClick(log._id);
                  }
                }}
                className={`sidebar-item group ${
                  currentLog?._id === log._id ? 'active' : ''
                } mb-1`}
              >
                <div className="flex items-center justify-between w-full">
                  <div className="flex items-center space-x-3 min-w-0 flex-1">
                    {getAircraftIcon(log.aircraft_registration)}
                    {isOpen && (
                      <div className="min-w-0 flex-1">
                        <div className="flex items-center space-x-2">
                          <p className="text-sm font-medium text-gray-900 truncate">
                            {log.aircraft_registration || 'Unknown'}
                          </p>
                          <span className={`text-xs font-medium ${getRiskColor(log.risk_level)}`}>
                            {log.risk_level || 'Unknown'}
                          </span>
                        </div>
                        <p className="text-xs text-gray-500 truncate">
                          {log.description || 'No description'}
                        </p>
                        <div className="flex items-center space-x-1 mt-1">
                          <Clock className="w-3 h-3 text-gray-400" />
                          <span className="text-xs text-gray-400">
                            {format(new Date(log.timestamp), 'MMM d, yyyy')}
                          </span>
                        </div>
                      </div>
                    )}
                  </div>
                  {isOpen && (
                    <button
                      onClick={(e) => {
                        e.preventDefault();
                        e.stopPropagation();
                        handleDeleteLog(e, log._id);
                      }}
                      className="p-2 rounded-md hover:bg-red-100 hover:text-red-600 transition-colors opacity-0 group-hover:opacity-100 focus:outline-none focus:ring-2 focus:ring-red-500"
                      title="Delete log"
                      type="button"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Footer */}
      {isOpen && (
        <div className="p-4 border-t border-gray-200">
          <div className="text-xs text-gray-500 text-center">
            {logs.length} maintenance log{logs.length !== 1 ? 's' : ''}
          </div>
        </div>
      )}
    </div>
  );
};

export default Sidebar; 