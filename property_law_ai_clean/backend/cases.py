from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import StreamingResponse
from typing import List, Optional
import logging
import io
from datetime import datetime

from models import (
    User, CaseCreate, CaseResponse, CaseListItem, CaseUpdate,
    DisputeType, CaseStatus, APIResponse
)
from database import get_database, Database
from auth import get_current_user
from ai_service import analyze_case_with_ai
from pdf_generator import generate_case_report_pdf

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/analyze-case", response_model=CaseResponse)
async def analyze_case(
    case_data: CaseCreate,
    current_user: User = Depends(get_current_user),
    db: Database = Depends(get_database)
):
    """Analyze a new case with AI"""
    try:
        logger.info(f"Starting case analysis for user: {current_user.email}")
        
        # Analyze case with AI
        ai_response = await analyze_case_with_ai(
            case_data.case_text,
            case_data.dispute_type
        )
        
        # Prepare case data for database
        case_record = {
            "user_id": current_user.id,
            "title": case_data.title,
            "case_text": case_data.case_text,
            "dispute_type": case_data.dispute_type.value,
            "ai_response": ai_response,
            "confidence_score": ai_response.get("confidence_score", 5),
            "status": "active"
        }
        
        # Save to database
        created_case = await db.create_case(case_record)
        
        logger.info(f"Case created successfully with ID: {created_case['id']}")
        
        # Return response
        return CaseResponse(
            id=created_case["id"],
            title=created_case["title"],
            case_text=created_case["case_text"],
            dispute_type=DisputeType(created_case["dispute_type"]),
            ai_response=ai_response,
            confidence_score=created_case["confidence_score"],
            status=CaseStatus(created_case["status"]),
            created_at=created_case["created_at"],
            updated_at=created_case.get("updated_at")
        )
        
    except Exception as e:
        logger.error(f"Case analysis failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Case analysis failed: {str(e)}"
        )

@router.get("/cases", response_model=List[CaseListItem])
async def get_user_cases(
    limit: int = 50,
    offset: int = 0,
    dispute_type: Optional[DisputeType] = None,
    current_user: User = Depends(get_current_user),
    db: Database = Depends(get_database)
):
    """Get user's case history"""
    try:
        logger.info(f"Fetching cases for user: {current_user.email}")
        
        # Get cases from database
        cases = await db.get_user_cases(current_user.id, limit, offset)
        
        # Filter by dispute type if specified
        if dispute_type:
            cases = [case for case in cases if case.get("dispute_type") == dispute_type.value]
        
        # Convert to response model
        case_list = []
        for case in cases:
            case_list.append(CaseListItem(
                id=case["id"],
                title=case["title"],
                dispute_type=DisputeType(case["dispute_type"]),
                confidence_score=case["confidence_score"],
                status=CaseStatus(case["status"]),
                created_at=case["created_at"]
            ))
        
        logger.info(f"Retrieved {len(case_list)} cases for user: {current_user.email}")
        return case_list
        
    except Exception as e:
        logger.error(f"Error fetching cases: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch cases"
        )

@router.get("/cases/{case_id}", response_model=CaseResponse)
async def get_case_details(
    case_id: str,
    current_user: User = Depends(get_current_user),
    db: Database = Depends(get_database)
):
    """Get detailed case information"""
    try:
        logger.info(f"Fetching case details: {case_id} for user: {current_user.email}")
        
        # Get case from database
        case = await db.get_case_by_id(case_id, current_user.id)
        
        if not case:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Case not found"
            )
        
        # Return detailed case information
        return CaseResponse(
            id=case["id"],
            title=case["title"],
            case_text=case["case_text"],
            dispute_type=DisputeType(case["dispute_type"]),
            ai_response=case["ai_response"],
            confidence_score=case["confidence_score"],
            status=CaseStatus(case["status"]),
            created_at=case["created_at"],
            updated_at=case.get("updated_at")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching case details: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch case details"
        )

@router.put("/cases/{case_id}", response_model=CaseResponse)
async def update_case(
    case_id: str,
    case_update: CaseUpdate,
    current_user: User = Depends(get_current_user),
    db: Database = Depends(get_database)
):
    """Update case information"""
    try:
        logger.info(f"Updating case: {case_id} for user: {current_user.email}")
        
        # Prepare update data
        update_data = {}
        if case_update.title is not None:
            update_data["title"] = case_update.title
        if case_update.case_text is not None:
            update_data["case_text"] = case_update.case_text
        if case_update.dispute_type is not None:
            update_data["dispute_type"] = case_update.dispute_type.value
        if case_update.status is not None:
            update_data["status"] = case_update.status.value
        
        # If case text or dispute type changed, re-analyze with AI
        if case_update.case_text is not None or case_update.dispute_type is not None:
            # Get current case data
            current_case = await db.get_case_by_id(case_id, current_user.id)
            if not current_case:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Case not found"
                )
            
            # Use updated values or current values
            case_text = case_update.case_text or current_case["case_text"]
            dispute_type = case_update.dispute_type or DisputeType(current_case["dispute_type"])
            
            # Re-analyze with AI
            ai_response = await analyze_case_with_ai(case_text, dispute_type)
            update_data["ai_response"] = ai_response
            update_data["confidence_score"] = ai_response.get("confidence_score", 5)
        
        # Update case in database
        updated_case = await db.update_case(case_id, current_user.id, update_data)
        
        if not updated_case:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Case not found"
            )
        
        logger.info(f"Case updated successfully: {case_id}")
        
        # Return updated case
        return CaseResponse(
            id=updated_case["id"],
            title=updated_case["title"],
            case_text=updated_case["case_text"],
            dispute_type=DisputeType(updated_case["dispute_type"]),
            ai_response=updated_case["ai_response"],
            confidence_score=updated_case["confidence_score"],
            status=CaseStatus(updated_case["status"]),
            created_at=updated_case["created_at"],
            updated_at=updated_case.get("updated_at")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating case: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update case"
        )

@router.delete("/cases/{case_id}")
async def delete_case(
    case_id: str,
    current_user: User = Depends(get_current_user),
    db: Database = Depends(get_database)
):
    """Delete (archive) a case"""
    try:
        logger.info(f"Deleting case: {case_id} for user: {current_user.email}")
        
        # Soft delete the case
        success = await db.delete_case(case_id, current_user.id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Case not found"
            )
        
        logger.info(f"Case deleted successfully: {case_id}")
        
        return {"message": "Case deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting case: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete case"
        )

@router.get("/cases/{case_id}/pdf")
async def download_case_pdf(
    case_id: str,
    current_user: User = Depends(get_current_user),
    db: Database = Depends(get_database)
):
    """Generate and download PDF report for a case"""
    try:
        logger.info(f"Generating PDF for case: {case_id} for user: {current_user.email}")
        
        # Get case data
        case = await db.get_case_by_id(case_id, current_user.id)
        
        if not case:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Case not found"
            )
        
        # Generate PDF
        pdf_buffer = await generate_case_report_pdf(case, current_user)
        
        # Create filename
        filename = f"case-report-{case_id}-{datetime.now().strftime('%Y%m%d')}.pdf"
        
        logger.info(f"PDF generated successfully for case: {case_id}")
        
        # Return PDF as streaming response
        return StreamingResponse(
            io.BytesIO(pdf_buffer),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating PDF: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate PDF report"
        )

@router.post("/cases/{case_id}/documents")
async def upload_case_document(
    case_id: str,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Database = Depends(get_database)
):
    """Upload a document for a case"""
    try:
        logger.info(f"Uploading document for case: {case_id}")
        
        # Verify case exists and belongs to user
        case = await db.get_case_by_id(case_id, current_user.id)
        if not case:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Case not found"
            )
        
        # Validate file
        if file.size > 10 * 1024 * 1024:  # 10MB limit
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="File size too large. Maximum 10MB allowed."
            )
        
        allowed_types = [
            "application/pdf",
            "image/jpeg",
            "image/png",
            "application/msword",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        ]
        
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File type not allowed"
            )
        
        # For now, we'll just return success
        # In production, you would save the file to cloud storage
        logger.info(f"Document upload successful for case: {case_id}")
        
        return {
            "message": "Document uploaded successfully",
            "filename": file.filename,
            "size": file.size,
            "type": file.content_type
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading document: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload document"
        )

@router.get("/stats")
async def get_user_stats(
    current_user: User = Depends(get_current_user),
    db: Database = Depends(get_database)
):
    """Get user statistics"""
    try:
        logger.info(f"Fetching stats for user: {current_user.email}")
        
        stats = await db.get_user_stats(current_user.id)
        
        return {
            "user": {
                "name": current_user.name,
                "email": current_user.email,
                "member_since": current_user.created_at
            },
            "statistics": stats
        }
        
    except Exception as e:
        logger.error(f"Error fetching user stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch statistics"
        )