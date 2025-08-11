from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

# Enums
class DisputeType(str, Enum):
    INHERITANCE = "inheritance"
    BOUNDARY = "boundary"
    MUTATION = "mutation"
    TAX = "tax"
    BBMP_BDA = "bbmp_bda"
    OTHER = "other"

class CaseStatus(str, Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"
    DELETED = "deleted"

# User Models
class UserBase(BaseModel):
    email: EmailStr
    name: str = Field(..., min_length=2, max_length=100)

class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=100)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class User(UserBase):
    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class UserInDB(User):
    hashed_password: str

# Token Models
class Token(BaseModel):
    access_token: str
    token_type: str
    user: User

class TokenData(BaseModel):
    email: Optional[str] = None

# Case Models
class CaseBase(BaseModel):
    title: str = Field(..., min_length=5, max_length=500)
    case_text: str = Field(..., min_length=50, max_length=10000)
    dispute_type: DisputeType

    @validator('case_text')
    def validate_case_text(cls, v):
        if len(v.strip()) < 50:
            raise ValueError('Case description must be at least 50 characters long')
        return v.strip()

class CaseCreate(CaseBase):
    pass

class CaseUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=5, max_length=500)
    case_text: Optional[str] = Field(None, min_length=50, max_length=10000)
    dispute_type: Optional[DisputeType] = None
    status: Optional[CaseStatus] = None

# AI Response Models
class CaseSummary(BaseModel):
    facts: str
    claims: str
    dispute_nature: str

class ApplicableLaw(BaseModel):
    law: str
    relevance: str

class LegalStrategies(BaseModel):
    plaintiff: Optional[List[str]] = []
    defendant: Optional[List[str]] = []

class Precedent(BaseModel):
    case: str
    relevance: str

class AIResponse(BaseModel):
    case_summary: CaseSummary
    legal_issues: List[str]
    applicable_laws: List[ApplicableLaw]
    missing_evidence: List[str]
    strategies: LegalStrategies
    confidence_score: int = Field(..., ge=1, le=10)
    next_steps: List[str]
    precedents: Optional[List[Precedent]] = []
    estimated_timeline: Optional[str] = None
    estimated_costs: Optional[str] = None

class Case(CaseBase):
    id: str
    user_id: str
    ai_response: AIResponse
    confidence_score: int
    status: CaseStatus = CaseStatus.ACTIVE
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class CaseResponse(BaseModel):
    id: str
    title: str
    case_text: str
    dispute_type: DisputeType
    ai_response: AIResponse
    confidence_score: int
    status: CaseStatus
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class CaseListItem(BaseModel):
    id: str
    title: str
    dispute_type: DisputeType
    confidence_score: int
    status: CaseStatus
    created_at: datetime

    class Config:
        from_attributes = True

# Document Models
class DocumentBase(BaseModel):
    file_name: str
    file_type: str
    file_size: int

class DocumentCreate(DocumentBase):
    file_path: str

class Document(DocumentBase):
    id: str
    case_id: str
    file_path: str
    uploaded_at: datetime

    class Config:
        from_attributes = True

# API Response Models
class APIResponse(BaseModel):
    success: bool = True
    message: str
    data: Optional[Any] = None

class ErrorResponse(BaseModel):
    success: bool = False
    message: str
    error_code: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

# Validation Models
class CaseAnalysisRequest(BaseModel):
    case_text: str = Field(..., min_length=50, max_length=10000)
    dispute_type: DisputeType
    
    @validator('case_text')
    def validate_case_text(cls, v):
        # Check for minimum meaningful content
        words = v.strip().split()
        if len(words) < 20:
            raise ValueError('Case description must contain at least 20 words')
        return v.strip()

# Statistics Models
class UserStats(BaseModel):
    total_cases: int
    cases_by_type: Dict[str, int]
    average_confidence: float
    recent_cases: List[CaseListItem]

class SystemStats(BaseModel):
    total_users: int
    total_cases: int
    cases_by_type: Dict[str, int]
    average_confidence: float