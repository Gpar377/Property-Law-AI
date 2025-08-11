from supabase import create_client, Client
import os
from dotenv import load_dotenv
import logging
from typing import Optional, Dict, Any, List
import asyncio
from datetime import datetime
import uuid

load_dotenv()

logger = logging.getLogger(__name__)

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")

# Create Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

class Database:
    def __init__(self):
        self.client = supabase

    async def init_db(self):
        """Initialize database tables"""
        try:
            # Check if tables exist by trying to query them
            await self.get_user_by_email("test@example.com")
            logger.info("Database connection successful")
        except Exception as e:
            logger.info("Database tables may need to be created")
            # In production, you would run the SQL schema here
            pass

    # User operations
    async def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new user"""
        try:
            user_data['id'] = str(uuid.uuid4())
            user_data['created_at'] = datetime.utcnow().isoformat()
            user_data['updated_at'] = datetime.utcnow().isoformat()
            
            result = self.client.table("users").insert(user_data).execute()
            
            if result.data:
                return result.data[0]
            else:
                raise Exception("Failed to create user")
                
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            raise

    async def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email"""
        try:
            result = self.client.table("users").select("*").eq("email", email).execute()
            
            if result.data:
                return result.data[0]
            return None
            
        except Exception as e:
            logger.error(f"Error getting user by email: {e}")
            return None

    async def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        try:
            result = self.client.table("users").select("*").eq("id", user_id).execute()
            
            if result.data:
                return result.data[0]
            return None
            
        except Exception as e:
            logger.error(f"Error getting user by ID: {e}")
            return None

    async def update_user(self, user_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update user"""
        try:
            update_data['updated_at'] = datetime.utcnow().isoformat()
            
            result = self.client.table("users").update(update_data).eq("id", user_id).execute()
            
            if result.data:
                return result.data[0]
            return None
            
        except Exception as e:
            logger.error(f"Error updating user: {e}")
            return None

    async def delete_user(self, user_id: str) -> bool:
        """Delete user and all associated data"""
        try:
            # Delete user (cascade will handle cases and documents)
            result = self.client.table("users").delete().eq("id", user_id).execute()
            return bool(result.data)
            
        except Exception as e:
            logger.error(f"Error deleting user: {e}")
            return False

    # Case operations
    async def create_case(self, case_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new case"""
        try:
            case_data['id'] = str(uuid.uuid4())
            case_data['created_at'] = datetime.utcnow().isoformat()
            case_data['updated_at'] = datetime.utcnow().isoformat()
            case_data['status'] = case_data.get('status', 'active')
            
            result = self.client.table("cases").insert(case_data).execute()
            
            if result.data:
                return result.data[0]
            else:
                raise Exception("Failed to create case")
                
        except Exception as e:
            logger.error(f"Error creating case: {e}")
            raise

    async def get_case_by_id(self, case_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Get case by ID for specific user"""
        try:
            result = self.client.table("cases").select("*").eq("id", case_id).eq("user_id", user_id).execute()
            
            if result.data:
                return result.data[0]
            return None
            
        except Exception as e:
            logger.error(f"Error getting case by ID: {e}")
            return None

    async def get_user_cases(self, user_id: str, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """Get all cases for a user"""
        try:
            result = (self.client.table("cases")
                     .select("*")
                     .eq("user_id", user_id)
                     .eq("status", "active")
                     .order("created_at", desc=True)
                     .limit(limit)
                     .offset(offset)
                     .execute())
            
            return result.data or []
            
        except Exception as e:
            logger.error(f"Error getting user cases: {e}")
            return []

    async def update_case(self, case_id: str, user_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update case"""
        try:
            update_data['updated_at'] = datetime.utcnow().isoformat()
            
            result = (self.client.table("cases")
                     .update(update_data)
                     .eq("id", case_id)
                     .eq("user_id", user_id)
                     .execute())
            
            if result.data:
                return result.data[0]
            return None
            
        except Exception as e:
            logger.error(f"Error updating case: {e}")
            return None

    async def delete_case(self, case_id: str, user_id: str) -> bool:
        """Soft delete case (mark as deleted)"""
        try:
            result = (self.client.table("cases")
                     .update({"status": "deleted", "updated_at": datetime.utcnow().isoformat()})
                     .eq("id", case_id)
                     .eq("user_id", user_id)
                     .execute())
            
            return bool(result.data)
            
        except Exception as e:
            logger.error(f"Error deleting case: {e}")
            return False

    # Document operations
    async def create_document(self, document_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new document"""
        try:
            document_data['id'] = str(uuid.uuid4())
            document_data['uploaded_at'] = datetime.utcnow().isoformat()
            
            result = self.client.table("case_documents").insert(document_data).execute()
            
            if result.data:
                return result.data[0]
            else:
                raise Exception("Failed to create document")
                
        except Exception as e:
            logger.error(f"Error creating document: {e}")
            raise

    async def get_case_documents(self, case_id: str) -> List[Dict[str, Any]]:
        """Get all documents for a case"""
        try:
            result = (self.client.table("case_documents")
                     .select("*")
                     .eq("case_id", case_id)
                     .order("uploaded_at", desc=True)
                     .execute())
            
            return result.data or []
            
        except Exception as e:
            logger.error(f"Error getting case documents: {e}")
            return []

    async def delete_document(self, document_id: str) -> bool:
        """Delete document"""
        try:
            result = self.client.table("case_documents").delete().eq("id", document_id).execute()
            return bool(result.data)
            
        except Exception as e:
            logger.error(f"Error deleting document: {e}")
            return False

    # Statistics operations
    async def get_user_stats(self, user_id: str) -> Dict[str, Any]:
        """Get user statistics"""
        try:
            # Get total cases
            cases_result = (self.client.table("cases")
                           .select("dispute_type,confidence_score")
                           .eq("user_id", user_id)
                           .eq("status", "active")
                           .execute())
            
            cases = cases_result.data or []
            total_cases = len(cases)
            
            # Calculate statistics
            cases_by_type = {}
            confidence_scores = []
            
            for case in cases:
                dispute_type = case.get('dispute_type', 'other')
                cases_by_type[dispute_type] = cases_by_type.get(dispute_type, 0) + 1
                
                if case.get('confidence_score'):
                    confidence_scores.append(case['confidence_score'])
            
            average_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
            
            return {
                "total_cases": total_cases,
                "cases_by_type": cases_by_type,
                "average_confidence": round(average_confidence, 2)
            }
            
        except Exception as e:
            logger.error(f"Error getting user stats: {e}")
            return {
                "total_cases": 0,
                "cases_by_type": {},
                "average_confidence": 0
            }

# Create database instance
db = Database()

# Dependency to get database
async def get_database() -> Database:
    return db

# Initialize database
async def init_db():
    """Initialize database"""
    await db.init_db()

# SQL Schema for reference (to be run in Supabase SQL editor)
SQL_SCHEMA = """
-- Users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Cases table
CREATE TABLE IF NOT EXISTS cases (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(500) NOT NULL,
    case_text TEXT NOT NULL,
    dispute_type VARCHAR(100) NOT NULL,
    ai_response JSONB NOT NULL,
    confidence_score INTEGER CHECK (confidence_score >= 1 AND confidence_score <= 10),
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Case documents table
CREATE TABLE IF NOT EXISTS case_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id UUID REFERENCES cases(id) ON DELETE CASCADE,
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_type VARCHAR(100) NOT NULL,
    file_size INTEGER,
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_cases_user_id ON cases(user_id);
CREATE INDEX IF NOT EXISTS idx_cases_dispute_type ON cases(dispute_type);
CREATE INDEX IF NOT EXISTS idx_cases_created_at ON cases(created_at);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_documents_case_id ON case_documents(case_id);

-- Enable Row Level Security
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE cases ENABLE ROW LEVEL SECURITY;
ALTER TABLE case_documents ENABLE ROW LEVEL SECURITY;

-- Create policies (optional - for additional security)
-- Users can only see their own data
CREATE POLICY "Users can view own profile" ON users FOR SELECT USING (auth.uid()::text = id);
CREATE POLICY "Users can update own profile" ON users FOR UPDATE USING (auth.uid()::text = id);

-- Users can only see their own cases
CREATE POLICY "Users can view own cases" ON cases FOR SELECT USING (auth.uid()::text = user_id);
CREATE POLICY "Users can insert own cases" ON cases FOR INSERT WITH CHECK (auth.uid()::text = user_id);
CREATE POLICY "Users can update own cases" ON cases FOR UPDATE USING (auth.uid()::text = user_id);
"""
