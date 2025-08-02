# Aircraft Maintenance Log Analyzer - System Documentation

## Project Overview
This is an AI-powered aircraft maintenance log analyzer that processes images of maintenance logs using GPT-4o Vision, extracts structured data, and provides an interactive interface for viewing, editing, and managing maintenance records.

## Backend Files

### `backend/main.py`
**Function**: Main FastAPI application entry point
- **Purpose**: Initializes the FastAPI app with CORS middleware and includes all routes
- **Key Functions**:
  - `app`: FastAPI application instance with CORS configuration
  - `lifespan`: Manages startup/shutdown events for database connection
- **Code Flow**: `app startup` → `database connection` → `routes registration` → `shutdown cleanup`

### `backend/database.py`
**Function**: MongoDB database connection and management
- **Purpose**: Manages MongoDB connection, collection access, and index creation
- **Key Functions**:
  - `Database.get_collection()`: Returns the maintenance logs collection
  - `Database.create_indexes()`: Creates database indexes for performance
- **Variables**:
  - `MONGODB_URL`: MongoDB connection string from environment
  - `DATABASE_NAME`: Database name from environment
  - `COLLECTION_NAME`: Collection name from environment
- **Usage**: Import and call `Database.get_collection()` to access the database

### `backend/models.py`
**Function**: Pydantic data models for validation and serialization
- **Purpose**: Defines data structures for maintenance logs, API requests/responses
- **Key Models**:
  - `LogEntry`: Individual maintenance log entry with fields like description, tach_time, risk_level, etc.
  - `MaintenanceLogData`: Top-level structured data containing aircraft info, summary, is_mult flag, and log_entries array
  - `MaintenanceLog`: Complete log document with metadata (timestamp, image_filename, etc.)
  - `LogSummary`: Sidebar summary view with aircraft registration, timestamp, description
  - `UploadResponse`: API response for upload operations
  - `ExportRequest`: Request model for export operations
- **Code Flow**: `AI response` → `MaintenanceLogData validation` → `MaintenanceLog creation` → `database storage`

### `backend/routes.py`
**Function**: FastAPI route definitions and API endpoints
- **Purpose**: Handles all HTTP requests for CRUD operations, file uploads, AI analysis, and exports
- **Key Endpoints**:
  - `POST /upload-log/`: Upload and analyze maintenance log images
  - `GET /logs/`: Get all logs for sidebar display
  - `GET /logs/{log_id}`: Get specific log details
  - `PUT /logs/{log_id}`: Update log data
  - `DELETE /logs/{log_id}`: Delete log
  - `POST /logs/{log_id}/export`: Export log as PDF
  - `GET /images/{image_filename}`: Serve uploaded images
- **Key Functions**:
  - `upload_maintenance_log()`: Processes image upload, calls AI analysis, saves to database
  - `get_all_logs()`: Retrieves logs for sidebar, extracts aircraft registration and description
  - `get_log_by_id()`: Gets full log details by ID
  - `update_log()`: Updates log data in database
  - `delete_log()`: Removes log from database
  - `export_log()`: Generates PDF export using reportlab
  - `generate_maintenance_log_pdf()`: Creates PDF with all log data
- **Variables**:
  - `API_BASE_URL`: Backend API URL from environment
- **Code Flow**: `HTTP request` → `route handler` → `database operation` → `response`

### `backend/ai_service.py`
**Function**: AI integration and image analysis
- **Purpose**: Handles OpenAI GPT-4o Vision API calls, image encoding, and structured data parsing
- **Key Functions**:
  - `analyze_maintenance_log()`: Main function that processes images with AI
  - `encode_image_to_base64()`: Converts image bytes to base64 for API
  - `get_system_prompt()`: Loads AI prompt from file
  - `validate_and_clean_data()`: Validates and cleans AI response data
  - `validate_new_format()`: Handles new format with log_entries array
  - `convert_old_to_new_format()`: Converts old single-entry format to new format
  - `fix_json_string()`: Fixes common JSON parsing issues
  - `extract_partial_json()`: Extracts data from truncated JSON responses with robust regex patterns
- **Helper Functions**:
  - `clean_log_entry()`: Cleans individual log entry data
  - `clean_string()`: Cleans string values with debug logging
  - `clean_part_numbers()`: Cleans part numbers array
  - `clean_boolean()`: Cleans boolean values with debug logging
- **Debug Features**:
  - Comprehensive debug logging throughout JSON parsing process
  - Multiple regex patterns for extracting summary and is_mult fields
  - Manual fallback extraction when regex patterns fail
  - JSON truncation detection and complete object extraction
  - Field presence checking before and after each processing step
- **Variables**:
  - `OPENAI_API_KEY`: OpenAI API key from environment
- **Code Flow**: `image bytes` → `base64 encoding` → `AI API call` → `JSON parsing` → `data cleaning` → `structured data`

### `backend/prompts/maintenance_log_analyzer.txt`
**Function**: AI system prompt for GPT-4o Vision
- **Purpose**: Defines the instructions for AI to extract structured data from maintenance log images
- **Content**: Detailed prompt explaining how to extract aircraft registration, make/model, summary, is_mult flag, and log_entries array
- **Usage**: Loaded by `ai_service.py` and sent to OpenAI API

### `backend/requirements.txt`
**Function**: Python dependencies list
- **Purpose**: Lists all required Python packages for pip installation
- **Key Dependencies**:
  - `fastapi`: Web framework
  - `uvicorn`: ASGI server
  - `motor`: Async MongoDB driver
  - `pymongo`: MongoDB driver
  - `openai`: OpenAI API client
  - `python-multipart`: File upload handling
  - `pillow`: Image processing
  - `reportlab`: PDF generation

### Debug Files (Temporary)
**Function**: Debugging tools for JSON parsing issues
- **Purpose**: Test and debug the summary field extraction problem
- **Files**:
  - `backend/test_json_parsing.py`: Comprehensive test of JSON parsing methods
  - `backend/debug_regex.py`: Regex pattern testing for summary/is_mult extraction
  - `backend/minimal_test.py`: Minimal test for summary field extraction
- **Current Issue**: Summary field not being saved despite being present in AI response
- **Debug Approach**: 
  - Multiple regex patterns for robust extraction
  - Manual fallback extraction when regex fails
  - Comprehensive logging at each processing step
  - JSON truncation detection and complete object extraction
  - `reportlab`: PDF generation
- **Usage**: `pip install -r requirements.txt`

### `backend/pyproject.toml`
**Function**: Project configuration and metadata
- **Purpose**: Defines project name, version, dependencies, and build settings
- **Usage**: Used by Hatchling for project management

## Frontend Files

### `frontend/src/components/LogDisplay.js`
**Function**: Main content panel for displaying and editing maintenance logs
- **Purpose**: Renders detailed log information with editing capabilities and image display
- **Key Functions**:
  - `handleEdit()`: Enables editing mode
  - `handleSave()`: Saves edited data to backend
  - `handleFieldChange()`: Updates top-level fields (aircraft_registration, aircraft_make_model, summary)
  - `handleEntryFieldChange()`: Updates fields within specific log entries
  - `handleArrayFieldChange()`: Updates array fields like part_number_replaced
  - `renderField()`: Renders top-level form fields
  - `renderEntryField()`: Renders fields within log entries
  - `renderLogEntry()`: Renders individual log entry with collapsible sections
  - `getHighestRiskLevel()`: Aggregates risk levels across all entries
  - `getHighestUrgency()`: Aggregates urgency levels across all entries
  - `getOverallAirworthiness()`: Determines overall airworthiness status
- **State Variables**:
  - `isEditing`: Boolean for edit mode
  - `editedData`: Current edited data state
  - `zoomLevel`: Image zoom level (0.5-3.0)
  - `expandedEntries`: Set of expanded entry indices
- **Code Flow**: `log data` → `render aircraft info` → `render summary (if is_mult)` → `render log entries` → `handle user interactions`

### `frontend/src/components/Sidebar.js`
**Function**: Sidebar component for displaying log history
- **Purpose**: Shows list of past logs with aircraft registration, timestamp, and description
- **Key Functions**:
  - `handleLogClick()`: Loads selected log for display
  - `handleDeleteLog()`: Deletes log from database
- **Code Flow**: `logs array` → `render log items` → `handle click/delete` → `update context`

### `frontend/src/components/FileUpload.js`
**Function**: File upload component with drag-and-drop functionality
- **Purpose**: Handles image file selection and upload to backend
- **Key Functions**:
  - `handleFileSelect()`: Processes selected files
  - `handleDrop()`: Handles drag-and-drop events
  - `handleUpload()`: Uploads file to backend API
- **State Variables**:
  - `isDragOver`: Boolean for drag state
  - `isUploading`: Boolean for upload progress
- **Code Flow**: `file selection` → `validation` → `upload to backend` → `update context`

### `frontend/src/context/MaintenanceLogContext.js`
**Function**: React context for global state management
- **Purpose**: Manages application state, API calls, and data flow
- **Key Functions**:
  - `fetchLogs()`: Retrieves all logs from backend
  - `uploadLog()`: Uploads new log and refreshes sidebar
  - `getLogById()`: Gets specific log by ID
  - `updateLog()`: Updates log and refreshes sidebar
  - `deleteLog()`: Deletes log and refreshes sidebar
  - `exportLog()`: Exports log as PDF
- **State Variables**:
  - `logs`: Array of log summaries for sidebar
  - `currentLog`: Currently selected log
  - `loading`: Loading state
  - `error`: Error state
- **Code Flow**: `API call` → `state update` → `component re-render`

### `frontend/src/App.js`
**Function**: Main application component
- **Purpose**: Renders the complete application layout with sidebar and main content
- **Key Functions**:
  - `renderMainContent()`: Renders appropriate content based on state
- **Code Flow**: `context state` → `render sidebar` → `render main content`

### `frontend/package.json`
**Function**: Node.js project configuration and dependencies
- **Purpose**: Defines frontend dependencies, scripts, and project metadata
- **Key Dependencies**:
  - `react`: UI library
  - `next`: React framework
  - `axios`: HTTP client
  - `lucide-react`: Icons
  - `date-fns`: Date formatting
  - `react-hot-toast`: Toast notifications
- **Usage**: `npm install` to install dependencies

## Environment Variables

### Backend (.env)
- `MONGODB_URL`: MongoDB connection string
- `DATABASE_NAME`: Database name
- `COLLECTION_NAME`: Collection name
- `OPENAI_API_KEY`: OpenAI API key
- `API_BASE_URL`: Backend API URL

### Frontend (.env.local)
- `NEXT_PUBLIC_API_BASE_URL`: Backend API URL for frontend

## Data Flow

1. **Upload Process**: `FileUpload` → `MaintenanceLogContext.uploadLog()` → `Backend upload endpoint` → `AI analysis` → `Database storage` → `Sidebar refresh`

2. **View Process**: `Sidebar click` → `MaintenanceLogContext.getLogById()` → `Backend get endpoint` → `LogDisplay render`

3. **Edit Process**: `LogDisplay edit` → `Field changes` → `MaintenanceLogContext.updateLog()` → `Backend update endpoint` → `Sidebar refresh`

4. **Delete Process**: `Sidebar delete` → `MaintenanceLogContext.deleteLog()` → `Backend delete endpoint` → `Sidebar refresh`

## Key Features

- **AI-Powered Analysis**: Uses GPT-4o Vision to extract structured data from maintenance log images
- **Multiple Entry Support**: Handles logs with multiple maintenance entries
- **Interactive Editing**: Edit all fields with real-time validation
- **PDF Export**: Generate professional PDF reports
- **Image Zoom**: Zoom in/out on original maintenance log images
- **Responsive Design**: Works on desktop and mobile devices
- **Real-time Updates**: Sidebar automatically refreshes after operations

## How to Use

1. **Upload**: Drag and drop or select a maintenance log image
2. **View**: Click on any log in the sidebar to view details
3. **Edit**: Click "Edit" button to modify log data
4. **Export**: Click "Export PDF" to download a PDF report
5. **Delete**: Click the delete button in sidebar to remove logs
6. **New Log**: Click "New Log" to start over

The system automatically processes images, extracts structured data, and provides a comprehensive interface for managing aircraft maintenance records. 