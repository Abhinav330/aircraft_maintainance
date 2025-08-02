from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import os
from dotenv import load_dotenv
from contextlib import asynccontextmanager
import logging

# Import our modules
from routes import router
from database import connect_to_mongo, close_mongo_connection

# Load environment variables
load_dotenv()

# Debug: Check if environment variables are loaded
print(f"=== ENVIRONMENT VARIABLES CHECK ===")
openai_key = os.getenv("OPENAI_API_KEY")
mongodb_url = os.getenv("MONGODB_URL")
db_name = os.getenv("MONGODB_DATABASE_NAME")
collection_name = os.getenv("MONGODB_COLLECTION_NAME")

print(f"📝 OPENAI_API_KEY: {'SET' if openai_key else 'NOT SET'}")
print(f"📝 MONGODB_URL: {'SET' if mongodb_url else 'NOT SET'}")
print(f"📝 MONGODB_DATABASE_NAME: {'SET' if db_name else 'NOT SET'}")
print(f"📝 MONGODB_COLLECTION_NAME: {'SET' if collection_name else 'NOT SET'}")

if not openai_key:
    print(f"❌ WARNING: OPENAI_API_KEY not found in environment variables")
if not mongodb_url:
    print(f"❌ WARNING: MONGODB_URL not found in environment variables")
if not db_name:
    print(f"❌ WARNING: MONGODB_DATABASE_NAME not found in environment variables")
if not collection_name:
    print(f"❌ WARNING: MONGODB_COLLECTION_NAME not found in environment variables")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"=== FASTAPI STARTUP ===")
    print(f"🔄 Connecting to MongoDB...")
    await connect_to_mongo()
    print(f"✅ MongoDB connected successfully")
    yield
    print(f"=== FASTAPI SHUTDOWN ===")
    print(f"🔄 Closing MongoDB connection...")
    await close_mongo_connection()
    print(f"✅ MongoDB connection closed")

# Create FastAPI app
app = FastAPI(
    title="Aircraft Maintenance Log Analyzer API",
    description="AI-powered aircraft maintenance log analysis and management",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
print(f"🔄 Including API routes...")
app.include_router(router)
print(f"✅ API routes included")

@app.get("/")
async def root():
    print(f"🔄 Health check endpoint called")
    return {"message": "Aircraft Maintenance Log Analyzer API", "status": "healthy"}

@app.get("/health")
async def health_check():
    print(f"🔄 Detailed health check endpoint called")
    return {
        "status": "healthy",
        "service": "Aircraft Maintenance Log Analyzer API",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    print(f"=== STARTING BACKEND SERVER ===")
    import uvicorn
    print(f"🔄 Starting uvicorn server on port 8000...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
