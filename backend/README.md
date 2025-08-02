# Aircraft Maintenance Log Analyzer - Backend

AI-powered backend service for analyzing aircraft maintenance logs using GPT-4o Vision.

## 🚀 Features

- **AI-Powered Analysis**: Uses GPT-4o Vision to extract structured data from maintenance log images
- **RESTful API**: Complete CRUD operations for maintenance logs
- **MongoDB Integration**: Persistent storage with proper indexing
- **Export Functionality**: JSON and PDF export capabilities
- **Search & Filter**: Search logs by aircraft registration
- **Validation**: Aircraft registration and data validation

## 🛠️ Tech Stack

- **FastAPI**: Modern, fast web framework for building APIs
- **MongoDB**: NoSQL database for flexible data storage
- **OpenAI GPT-4o**: Vision model for image analysis
- **Pydantic**: Data validation and serialization
- **Uvicorn**: ASGI server for production deployment

## 📋 Prerequisites

- Python 3.11+
- MongoDB (local or cloud)
- OpenAI API key

## 🔧 Installation

1. **Clone the repository**
   ```bash
   cd backend
   ```

2. **Install dependencies**
   ```bash
   pip install -e .
   ```

3. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your actual credentials
   ```

4. **Start MongoDB** (if using local)
   ```bash
   # Install MongoDB locally or use MongoDB Atlas
   ```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key_here

# MongoDB Configuration
MONGODB_URL=mongodb://localhost:27017

# Application Configuration
ENVIRONMENT=development
DEBUG=true
```

## 🚀 Running the Application

### Development Mode
```bash
python main.py
```

### Production Mode
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

## 📚 API Documentation

Once running, visit:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## 🔌 API Endpoints

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/upload-log/` | Upload and analyze maintenance log image |
| `GET` | `/api/v1/logs/` | Get all logs (summary view) |
| `GET` | `/api/v1/logs/{log_id}` | Get specific log details |
| `PUT` | `/api/v1/logs/{log_id}` | Update log data |
| `DELETE` | `/api/v1/logs/{log_id}` | Delete log |
| `POST` | `/api/v1/logs/{log_id}/export` | Export log to JSON/PDF |
| `GET` | `/api/v1/logs/search/{registration}` | Search by aircraft registration |

### Health Check
- `GET /` - API health check
- `GET /health` - Detailed health status

## 📊 Data Models

### MaintenanceLogData
```json
{
  "description_of_work_performed": "string",
  "aircraft_registration": "string",
  "aircraft_make_model": "string",
  "tach_time": "string",
  "hobbs_time": "string",
  "part_number_replaced": ["string"],
  "manual_reference": "string",
  "reason_for_maintenance": "string",
  "ad_compliance": "string",
  "next_due_compliance": "string",
  "service_bulletin_reference": "string",
  "certification_statement": "string",
  "performed_by": "string",
  "license_number": "string",
  "date": "string",
  "risk_level": "string",
  "urgency": "string",
  "is_airworthy": true
}
```

## 🔍 AI Analysis Features

### GPT-4o Vision Integration
- **Image Analysis**: Extracts structured data from handwritten/printed logs
- **Validation**: Aircraft registration format validation
- **Risk Assessment**: Automatic risk level determination
- **Urgency Detection**: Identifies critical maintenance items

### Supported Image Formats
- JPEG/JPG
- PNG
- WebP
- Other common image formats

## 🗄️ Database Schema

### Collection: `maintenance_logs`
```json
{
  "_id": "ObjectId",
  "uploaded_by": "string",
  "timestamp": "datetime",
  "image_filename": "string",
  "structured_data": "MaintenanceLogData",
  "original_image_url": "string"
}
```

## 🔒 Security Considerations

- **API Key Protection**: Store OpenAI API key in environment variables
- **Input Validation**: All inputs are validated using Pydantic
- **Error Handling**: Comprehensive error handling and logging
- **CORS Configuration**: Proper CORS setup for frontend integration

## 🧪 Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=.
```

## 📦 Deployment

### Docker (Recommended)
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Variables for Production
```env
ENVIRONMENT=production
DEBUG=false
MONGODB_URL=mongodb://your-production-mongodb-url
OPENAI_API_KEY=your-production-openai-key
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.
