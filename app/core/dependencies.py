from datetime import date
from fastapi import HTTPException, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.repositories.waste_report import WasteReportRepository
from app.db.models.user import User
from app.api.dependencies import get_current_user


# Rate limiting constants
MAX_REPORTS_PER_DAY = 10


async def check_rate_limit(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> User:
    """Check if user has exceeded daily report creation limit"""
    reports_today = WasteReportRepository.count_user_reports_today(db, current_user.id)
    
    if reports_today >= MAX_REPORTS_PER_DAY:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Daily limit of {MAX_REPORTS_PER_DAY} waste reports exceeded. Please try again tomorrow."
        )
    
    return current_user


async def get_current_admin_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Verify that the current user is an admin"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


async def check_report_ownership(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> User:
    """Check if user owns the waste report"""
    report = WasteReportRepository.get(db, report_id)
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Waste report not found"
        )
    
    if report.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only access your own waste reports"
        )
    
    return current_user


async def check_edit_permission(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> User:
    """Check if user can edit the waste report"""
    if current_user.is_superuser:
        return current_user
    
    if not WasteReportRepository.can_user_edit(db, report_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only edit your own pending waste reports"
        )
    
    return current_user


async def check_delete_permission(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> User:
    """Check if user can delete the waste report"""
    if current_user.is_superuser:
        return current_user
    
    if not WasteReportRepository.can_user_delete(db, report_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own pending waste reports"
        )
    
    return current_user
