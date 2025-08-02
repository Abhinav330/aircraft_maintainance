# 🛩️ AI-Powered Aircraft Maintenance Log Analyzer

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-14.0+-black.svg)](https://nextjs.org)
[![React](https://img.shields.io/badge/React-18.2+-blue.svg)](https://reactjs.org)
[![MongoDB](https://img.shields.io/badge/MongoDB-6.0+-green.svg)](https://mongodb.com)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o--Vision-orange.svg)](https://openai.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **Revolutionary AI-powered solution for extracting structured data from aircraft maintenance logs using computer vision and natural language processing.**

## 🚀 Features

### ✨ Core Capabilities
- **🔍 AI-Powered Analysis**: Uses OpenAI GPT-4o Vision to extract structured data from handwritten and printed maintenance logs
- **📱 Modern Web Interface**: Responsive Next.js frontend with drag-and-drop file upload
- **🔄 Real-time Processing**: Instant analysis and structured data extraction
- **📊 Multiple Entry Support**: Handles single and multiple maintenance entries with intelligent summarization
- **🖼️ Image Management**: Upload, display, zoom, and pan through maintenance log images
- **📄 Export Capabilities**: Export logs as JSON or professionally formatted PDF reports

### 🎯 Advanced Features
- **🔍 Smart Data Extraction**: Automatically identifies aircraft registration, make/model, technician details, work performed, and risk assessments
- **📋 Structured Output**: Consistent JSON format with validated data fields
- **🎨 Interactive UI**: Zoom and pan functionality for detailed image inspection
- **📱 Responsive Design**: Works seamlessly on desktop, tablet, and mobile devices
- **⚡ Real-time Updates**: Live sidebar updates and instant feedback
- **🔒 Secure Storage**: MongoDB-based data persistence with proper indexing

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Next.js       │    │   FastAPI       │    │   MongoDB       │
│   Frontend      │◄──►│   Backend       │◄──►│   Database      │
│                 │    │                 │    │                 │
│ • React 18      │    │ • Python 3.8+   │    │ • Document Store│
│ • Tailwind CSS  │    │ • FastAPI       │    │ • Indexed       │
│ • Dropzone      │    │ • Motor/PyMongo │    │ • Scalable      │
│ • PDF Export    │    │ • OpenAI API    │    │ • ACID Compliant│
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🛠️ Technology Stack

### Backend
- **FastAPI** - Modern, fast web framework for building APIs
- **Python 3.8+** - High-level programming language
- **Motor** - Async MongoDB driver for Python
- **Pydantic v2** - Data validation and serialization
- **OpenAI GPT-4o Vision** - Advanced AI model for image analysis
- **ReportLab** - Professional PDF generation
- **Uvicorn** - Lightning-fast ASGI server

### Frontend
- **Next.js 14** - React framework with SSR capabilities
- **React 18** - JavaScript library for building user interfaces
- **Tailwind CSS** - Utility-first CSS framework
- **Lucide React** - Beautiful & consistent icon toolkit
- **React Dropzone** - Drag and drop file upload
- **React Hot Toast** - Elegant notifications
- **Axios** - Promise-based HTTP client

### Database
- **MongoDB** - NoSQL document database
- **Motor** - Async MongoDB driver
- **Indexed Collections** - Optimized query performance

## 📦 Installation

### Prerequisites
- **Python 3.8+**
- **Node.js 18+**
- **MongoDB 6.0+**
- **OpenAI API Key**

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/aircraft-maintenance-analyzer.git
cd aircraft-maintenance-analyzer
```

### 2. Backend Setup
```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp env.example .env

# Edit .env file with your configuration
# See Configuration section below
```

### 3. Frontend Setup
```bash
# Navigate to frontend directory
cd ../frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### 4. Database Setup
```bash
# Start MongoDB (if not running)
mongod

# The application will automatically create collections and indexes
```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the `backend` directory:

```env
# OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key_here

# MongoDB Configuration
MONGODB_URL=mongodb://localhost:27017
MONGODB_DATABASE_NAME=aircraft_maintenance
MONGODB_COLLECTION_NAME=maintenance_logs

# Application Configuration
ENVIRONMENT=development
DEBUG=true

# Server Configuration
HOST=0.0.0.0
PORT=8000

# CORS Configuration
FRONTEND_URL=http://localhost:3000
```

### Getting OpenAI API Key
1. Visit [OpenAI Platform](https://platform.openai.com/)
2. Create an account or sign in
3. Navigate to API Keys section
4. Create a new API key
5. Copy the key to your `.env` file

## 🚀 Running the Application

### Development Mode

1. **Start Backend Server**
```bash
cd backend
python main.py
```
Server will start at `http://localhost:8000`

2. **Start Frontend Development Server**
```bash
cd frontend
npm run dev
```
Frontend will start at `http://localhost:3000`

3. **Access the Application**
Open your browser and navigate to `http://localhost:3000`

### Production Mode

1. **Build Frontend**
```bash
cd frontend
npm run build
npm start
```

2. **Run Backend with Production Server**
```bash
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000
```

## 📖 Usage

### 1. Upload Maintenance Log
- Drag and drop an image file or click "Choose File"
- Supported formats: JPEG, PNG, WebP, TIFF
- Maximum file size: 10MB

### 2. AI Analysis
- The system automatically analyzes the uploaded image
- Extracts structured data using GPT-4o Vision
- Processes both handwritten and printed logs

### 3. View Results
- Review extracted data in a structured format
- Edit any fields if needed
- View the original image with zoom/pan capabilities

### 4. Export Data
- Export as JSON for data processing
- Export as PDF for regulatory compliance
- Professional formatting with all maintenance details

## 🔧 API Endpoints

### Core Endpoints
- `POST /api/upload` - Upload and analyze maintenance log
- `GET /api/logs` - Retrieve all maintenance logs
- `GET /api/logs/{log_id}` - Get specific log details
- `PUT /api/logs/{log_id}` - Update log information
- `DELETE /api/logs/{log_id}` - Delete log
- `GET /api/logs/{log_id}/export` - Export log as PDF

### Utility Endpoints
- `GET /images/{filename}` - Serve uploaded images
- `GET /health` - Health check endpoint
- `GET /` - API information

## 📊 Data Structure

### Maintenance Log Format
```json
{
  "aircraft_registration": "N12345",
  "aircraft_make_model": "Boeing 737-800",
  "summary": "Multiple maintenance tasks performed",
  "is_mult": true,
  "log_entries": [
    {
      "date": "2024-01-15",
      "technician_name": "John Smith",
      "technician_id": "TS001",
      "work_performed": "Engine oil change and filter replacement",
      "risk_level": "Low",
      "urgency": "Medium",
      "part_numbers_replaced": ["OIL-FILTER-001", "ENGINE-OIL-5W30"],
      "reason_for_maintenance": "Scheduled maintenance"
    }
  ]
}
```

## 🎯 Supported Maintenance Log Types

### Aircraft Information
- Aircraft registration number
- Make and model
- Serial number
- Flight hours

### Maintenance Details
- Work performed description
- Date and time of maintenance
- Technician information
- Risk assessment
- Urgency level

### Parts and Materials
- Part numbers replaced
- Materials used
- Quantities and specifications

### Regulatory Compliance
- Maintenance type classification
- Regulatory references
- Certification requirements

## 🔒 Security Features

- **Environment Variables** - Sensitive data stored securely
- **CORS Protection** - Cross-origin request security
- **Input Validation** - Pydantic data validation
- **Error Handling** - Comprehensive error management
- **Logging** - Detailed application logging

## 🧪 Testing

### Backend Testing
```bash
cd backend
python -m pytest tests/
```

### Frontend Testing
```bash
cd frontend
npm test
```

## 📈 Performance

- **FastAPI** - One of the fastest Python web frameworks
- **Async Operations** - Non-blocking database operations
- **Optimized Queries** - Indexed MongoDB collections
- **CDN Ready** - Static asset optimization
- **Caching** - Intelligent data caching

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/amazing-feature`)
3. **Commit your changes** (`git commit -m 'Add amazing feature'`)
4. **Push to the branch** (`git push origin feature/amazing-feature`)
5. **Open a Pull Request**

### Development Guidelines
- Follow PEP 8 for Python code
- Use ESLint for JavaScript/TypeScript
- Write comprehensive tests
- Update documentation
- Ensure all tests pass

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **OpenAI** - For providing GPT-4o Vision API
- **FastAPI** - For the excellent web framework
- **Next.js** - For the React framework
- **MongoDB** - For the database solution
- **Tailwind CSS** - For the utility-first CSS framework


## 🚀 Roadmap

- [ ] **Multi-language Support** - Internationalization
- [ ] **Advanced Analytics** - Maintenance trend analysis
- [ ] **Mobile App** - Native iOS/Android applications
- [ ] **Cloud Deployment** - AWS/Azure integration
- [ ] **Machine Learning** - Custom model training
- [ ] **API Rate Limiting** - Enhanced security
- [ ] **WebSocket Support** - Real-time updates
- [ ] **Bulk Upload** - Multiple file processing

---

<div align="center">

**Made with ❤️ for the aviation industry**

[![GitHub stars](https://img.shields.io/github/stars/Abhinav330/aircraft_maintainance?style=social)]((https://github.com/Abhinav330/aircraft_maintainance))
[![GitHub forks](https://img.shields.io/github/forks/Abhinav330/aircraft_maintainance?style=social)](https://github.com/Abhinav330/aircraft_maintainance)
[![GitHub issues](https://img.shields.io/github/issues/Abhinav330/aircraft_maintainance)](https://github.com/Abhinav330/aircraft_maintainance)

</div>

