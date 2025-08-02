import os
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient, DESCENDING
from bson import ObjectId

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Database:
    client: AsyncIOMotorClient = None
    database_name: str = None
    collection_name: str = None

    @classmethod
    def connect_db(cls):
        print(f"=== DATABASE CONNECTION START ===")
        try:
            # Get environment variables
            mongodb_url = os.getenv("MONGODB_URL")
            cls.database_name = os.getenv("MONGODB_DATABASE_NAME")
            cls.collection_name = os.getenv("MONGODB_COLLECTION_NAME")
            
            print(f"📝 MongoDB URL: {mongodb_url}")
            print(f"📝 Database name: {cls.database_name}")
            print(f"📝 Collection name: {cls.collection_name}")
            
            if not mongodb_url or not cls.database_name or not cls.collection_name:
                print(f"❌ Missing environment variables")
                raise ValueError("Missing required environment variables: MONGODB_URL, MONGODB_DATABASE_NAME, MONGODB_COLLECTION_NAME")
            
            # Create async client
            cls.client = AsyncIOMotorClient(mongodb_url)
            print(f"✅ Async MongoDB client created")
            
            # Test connection
            print(f"🔄 Testing database connection...")
            # Use sync client for testing
            sync_client = MongoClient(mongodb_url)
            sync_client.admin.command('ping')
            print(f"✅ Database connection test passed")
            sync_client.close()
            
            # Create indexes
            print(f"🔄 Creating database indexes...")
            cls.create_indexes()
            print(f"✅ Database indexes created")
            
        except Exception as e:
            print(f"❌ ERROR in connect_db: {e}")
            import traceback
            print(f"❌ ERROR traceback: {traceback.format_exc()}")
            raise e

    @classmethod
    def close_db(cls):
        print(f"=== DATABASE CLOSE ===")
        if cls.client:
            cls.client.close()
            print(f"✅ Database connection closed")

    @classmethod
    def get_collection(cls):
        print(f"🔄 Getting collection: {cls.collection_name}")
        if not cls.client:
            print(f"❌ Database client not initialized")
            raise RuntimeError("Database not connected")
        
        database = cls.client[cls.database_name]
        collection = database[cls.collection_name]
        print(f"✅ Collection obtained: {collection.name}")
        return collection

    @classmethod
    def create_indexes(cls):
        print(f"=== CREATE INDEXES START ===")
        try:
            # Use synchronous client for index creation
            mongodb_url = os.getenv("MONGODB_URL")
            sync_client = MongoClient(mongodb_url)
            database = sync_client[cls.database_name]
            collection = database[cls.collection_name]
            
            print(f"✅ Sync client created for index creation")
            
            # Create indexes using proper PyMongo methods
            indexes_to_create = [
                ("timestamp", DESCENDING),
                ("aircraft_registration", 1),
                ("uploaded_by", 1)
            ]
            
            for field, direction in indexes_to_create:
                try:
                    print(f"🔄 Creating index on {field} with direction {direction}")
                    
                    # Use create_index with background=True and sparse=True for better handling
                    collection.create_index(
                        [(field, direction)], 
                        background=True,
                        sparse=True
                    )
                    print(f"✅ Index created on {field}")
                        
                except Exception as e:
                    # Check if it's a duplicate index error (which is fine)
                    error_str = str(e).lower()
                    if ("already exists" in error_str or 
                        "duplicate" in error_str or 
                        "indexkeyspecsconflict" in error_str or
                        "code: 86" in error_str or
                        "same name as the requested index" in error_str):
                        print(f"✅ Index on {field} already exists")
                    else:
                        print(f"⚠️ Warning: Failed to create index on {field}: {e}")
                    # Don't fail startup for index creation issues
                    pass
            
            sync_client.close()
            print(f"✅ Index creation completed")
            
        except Exception as e:
            print(f"❌ ERROR in create_indexes: {e}")
            import traceback
            print(f"❌ ERROR traceback: {traceback.format_exc()}")
            # Don't fail startup for index creation issues
            pass

# Database connection event handlers
async def connect_to_mongo():
    """Connect to MongoDB on startup"""
    Database.connect_db()
    # Indexes are already created in connect_db(), no need to call again

async def close_mongo_connection():
    """Close MongoDB connection on shutdown"""
    Database.close_db() 