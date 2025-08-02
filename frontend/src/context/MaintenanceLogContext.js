import React, { createContext, useContext, useReducer, useEffect } from 'react';
import { toast } from 'react-hot-toast';
import axios from 'axios';

// API base URL
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

// Initial state
const initialState = {
  logs: [],
  currentLog: null,
  loading: false,
  error: null,
  uploading: false,
  analyzing: false,
};

// Action types
const ACTIONS = {
  SET_LOADING: 'SET_LOADING',
  SET_ERROR: 'SET_ERROR',
  SET_LOGS: 'SET_LOGS',
  SET_CURRENT_LOG: 'SET_CURRENT_LOG',
  ADD_LOG: 'ADD_LOG',
  UPDATE_LOG: 'UPDATE_LOG',
  DELETE_LOG: 'DELETE_LOG',
  SET_UPLOADING: 'SET_UPLOADING',
  SET_ANALYZING: 'SET_ANALYZING',
  CLEAR_ERROR: 'CLEAR_ERROR',
};

// Reducer
function maintenanceLogReducer(state, action) {
  switch (action.type) {
    case ACTIONS.SET_LOADING:
      return { ...state, loading: action.payload };
    
    case ACTIONS.SET_ERROR:
      return { ...state, error: action.payload, loading: false };
    
    case ACTIONS.SET_LOGS:
      return { ...state, logs: action.payload, loading: false };
    
    case ACTIONS.SET_CURRENT_LOG:
      return { ...state, currentLog: action.payload, loading: false };
    
    case ACTIONS.ADD_LOG:
      return { 
        ...state, 
        logs: [action.payload, ...state.logs],
        currentLog: action.payload,
        uploading: false,
        analyzing: false 
      };
    
    case ACTIONS.UPDATE_LOG:
      return {
        ...state,
        logs: state.logs.map(log => 
          log._id === action.payload._id ? action.payload : log
        ),
        currentLog: action.payload,
      };
    
    case ACTIONS.DELETE_LOG:
      return {
        ...state,
        logs: state.logs.filter(log => log._id !== action.payload),
        currentLog: state.currentLog?._id === action.payload ? null : state.currentLog,
      };
    
    case ACTIONS.SET_UPLOADING:
      return { ...state, uploading: action.payload };
    
    case ACTIONS.SET_ANALYZING:
      return { ...state, analyzing: action.payload };
    
    case ACTIONS.CLEAR_ERROR:
      return { ...state, error: null };
    
    default:
      return state;
  }
}

// Create context
const MaintenanceLogContext = createContext();

// Provider component
export function MaintenanceLogProvider({ children }) {
  const [state, dispatch] = useReducer(maintenanceLogReducer, initialState);

  // Load logs on mount
  useEffect(() => {
    fetchLogs();
  }, []);

  // API functions
  const fetchLogs = async () => {
    try {
      dispatch({ type: ACTIONS.SET_LOADING, payload: true });
      const response = await axios.get(`${API_BASE_URL}/logs/`);
      dispatch({ type: ACTIONS.SET_LOGS, payload: response.data });
    } catch (error) {
      console.error('Error fetching logs:', error);
      dispatch({ 
        type: ACTIONS.SET_ERROR, 
        payload: 'Failed to fetch maintenance logs' 
      });
      toast.error('Failed to fetch maintenance logs');
    }
  };

  const fetchLogById = async (logId) => {
    console.log('=== FETCH LOG BY ID START ===', logId);
    try {
      dispatch({ type: ACTIONS.SET_LOADING, payload: true });
      console.log('🔄 Making API request to:', `${API_BASE_URL}/logs/${logId}`);
      
      const response = await axios.get(`${API_BASE_URL}/logs/${logId}`);
      console.log('✅ API response received:', response.data);
      
      dispatch({ type: ACTIONS.SET_CURRENT_LOG, payload: response.data });
      console.log('✅ SET_CURRENT_LOG action dispatched');
    } catch (error) {
      console.error('❌ ERROR in fetchLogById:', error);
      console.error('❌ Error response:', error.response);
      console.error('❌ Error status:', error.response?.status);
      console.error('❌ Error data:', error.response?.data);
      
      dispatch({ 
        type: ACTIONS.SET_ERROR, 
        payload: 'Failed to load maintenance log' 
      });
      toast.error('Failed to load maintenance log');
    }
  };

  const uploadLog = async (file) => {
    try {
      dispatch({ type: ACTIONS.SET_UPLOADING, payload: true });
      dispatch({ type: ACTIONS.SET_ANALYZING, payload: true });

      const formData = new FormData();
      formData.append('file', file);

      const response = await axios.post(`${API_BASE_URL}/upload-log/`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      if (response.data.success) {
        // Fetch the complete log data
        const logResponse = await axios.get(`${API_BASE_URL}/logs/${response.data.log_id}`);
        dispatch({ type: ACTIONS.ADD_LOG, payload: logResponse.data });
        
        // Refresh the logs list to ensure sidebar shows correct data
        await fetchLogs();
        
        toast.success('Maintenance log analyzed successfully!');
      } else {
        throw new Error(response.data.message || 'Upload failed');
      }
    } catch (error) {
      console.error('Error uploading log:', error);
      dispatch({ 
        type: ACTIONS.SET_ERROR, 
        payload: 'Failed to analyze maintenance log' 
      });
      toast.error('Failed to analyze maintenance log');
    }
  };

  const updateLog = async (logId, logData) => {
    try {
      const response = await axios.put(`${API_BASE_URL}/logs/${logId}`, logData);
      dispatch({ type: ACTIONS.UPDATE_LOG, payload: response.data });
      
      // Refresh the logs list to ensure sidebar shows correct data
      await fetchLogs();
      
      toast.success('Maintenance log updated successfully!');
    } catch (error) {
      console.error('Error updating log:', error);
      dispatch({ 
        type: ACTIONS.SET_ERROR, 
        payload: 'Failed to update maintenance log' 
      });
      toast.error('Failed to update maintenance log');
    }
  };

  const deleteLog = async (logId) => {
    try {
      const response = await axios.delete(`${API_BASE_URL}/logs/${logId}`);
      dispatch({ type: ACTIONS.DELETE_LOG, payload: logId });
      toast.success('Maintenance log deleted successfully!');
    } catch (error) {
      console.error('Error deleting log:', error);
      dispatch({ 
        type: ACTIONS.SET_ERROR, 
        payload: 'Failed to delete maintenance log' 
      });
      toast.error('Failed to delete maintenance log');
    }
  };

  const exportLog = async (logId, format) => {
    try {
      const response = await axios.post(`${API_BASE_URL}/logs/${logId}/export`, {
        format: format,
        log_id: logId
      }, {
        responseType: 'blob'
      });

      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `maintenance_log_${logId}.${format}`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);

      toast.success(`${format.toUpperCase()} export successful!`);
    } catch (error) {
      console.error('Error exporting log:', error);
      toast.error(`Failed to export ${format.toUpperCase()}`);
    }
  };

  const searchLogs = async (aircraftRegistration) => {
    try {
      dispatch({ type: ACTIONS.SET_LOADING, payload: true });
      const response = await axios.get(`${API_BASE_URL}/logs/search/${aircraftRegistration}`);
      dispatch({ type: ACTIONS.SET_LOGS, payload: response.data });
    } catch (error) {
      console.error('Error searching logs:', error);
      dispatch({ 
        type: ACTIONS.SET_ERROR, 
        payload: 'Failed to search maintenance logs' 
      });
      toast.error('Failed to search maintenance logs');
    }
  };

  const clearError = () => {
    dispatch({ type: ACTIONS.CLEAR_ERROR });
  };

  const clearCurrentLog = () => {
    dispatch({ type: ACTIONS.SET_CURRENT_LOG, payload: null });
  };

  const value = {
    ...state,
    fetchLogs,
    fetchLogById,
    uploadLog,
    updateLog,
    deleteLog,
    exportLog,
    searchLogs,
    clearError,
    clearCurrentLog,
  };

  return (
    <MaintenanceLogContext.Provider value={value}>
      {children}
    </MaintenanceLogContext.Provider>
  );
}

// Custom hook to use the context
export function useMaintenanceLog() {
  const context = useContext(MaintenanceLogContext);
  if (!context) {
    throw new Error('useMaintenanceLog must be used within a MaintenanceLogProvider');
  }
  return context;
} 