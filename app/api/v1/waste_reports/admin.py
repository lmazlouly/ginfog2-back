from datetime import date
from typing import Any, List, Optional
from math import ceil

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_admin_user
from app.db.repositories.waste_report import WasteReportRepository
from app.db.session import get_db
from app.db.models.user import User
from app.db.models.enums import WasteType, ReportStatus, UrgencyLevel
from app.schemas.waste_report import (
    WasteReportAdminResponse, WasteReportStatusUpdate, 
    WasteReportList, WasteReportListItem
)

router = APIRouter(prefix="/admin/waste-reports", tags=["admin", "waste-reports"])


@router.get("", response_model=WasteReportList, operation_id="adminGetAllWasteReports")
def get_all_waste_reports(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Items per page"),
    status: Optional[ReportStatus] = Query(None, description="Filter by status"),
    waste_type: Optional[WasteType] = Query(None, description="Filter by waste type"),
    urgency_level: Optional[UrgencyLevel] = Query(None, description="Filter by urgency level"),
    date_from: Optional[date] = Query(None, description="Filter from date (YYYY-MM-DD)"),
    date_to: Optional[date] = Query(None, description="Filter to date (YYYY-MM-DD)"),
    city: Optional[str] = Query(None, description="Filter by city"),
    sort_by: str = Query("created_at", description="Sort by field"),
    sort_order: str = Query("desc", regex="^(asc|desc)$", description="Sort order")
) -> Any:
    """
    Get all waste reports for admin with advanced filtering, pagination, and sorting.
    Admin only endpoint.
    """
    skip = (page - 1) * size
    
    items, total = WasteReportRepository.get_multi_admin(
        db=db,
        skip=skip,
        limit=size,
        status=status,
        waste_type=waste_type,
        urgency_level=urgency_level,
        date_from=date_from,
        date_to=date_to,
        city=city,
        sort_by=sort_by,
        sort_order=sort_order
    )
    
    # Convert to list items with photo count and user info
    list_items = []
    for item in items:
        list_item = WasteReportListItem(
            id=item.id,
            street_address=item.street_address,
            city=item.city,
            waste_type=item.waste_type,
            urgency_level=item.urgency_level,
            status=item.status,
            created_at=item.created_at,
            photo_count=len(item.photos) if item.photos else 0
        )
        list_items.append(list_item)
    
    pages = ceil(total / size) if total > 0 else 1
    
    return WasteReportList(
        items=list_items,
        total=total,
        page=page,
        size=size,
        pages=pages
    )


@router.get("/{report_id}", response_model=WasteReportAdminResponse, operation_id="adminGetWasteReport")
def get_waste_report_admin(
    *,
    db: Session = Depends(get_db),
    report_id: int,
    current_user: User = Depends(get_current_admin_user)
) -> Any:
    """
    Get a specific waste report by ID with user information.
    Admin only endpoint.
    """
    waste_report = WasteReportRepository.get_with_user(db=db, waste_report_id=report_id)
    if not waste_report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Waste report not found"
        )
    
    # Create admin response with user information
    admin_response = WasteReportAdminResponse(
        id=waste_report.id,
        user_id=waste_report.user_id,
        street_address=waste_report.street_address,
        city=waste_report.city,
        postal_code=waste_report.postal_code,
        latitude=waste_report.latitude,
        longitude=waste_report.longitude,
        waste_type=waste_report.waste_type,
        quantity_estimate=waste_report.quantity_estimate,
        urgency_level=waste_report.urgency_level,
        description=waste_report.description,
        reporter_name=waste_report.reporter_name,
        reporter_phone=waste_report.reporter_phone,
        status=waste_report.status,
        admin_notes=waste_report.admin_notes,
        created_at=waste_report.created_at,
        updated_at=waste_report.updated_at,
        photos=[
            {
                "id": photo.id,
                "waste_report_id": photo.waste_report_id,
                "photo_url": photo.photo_url,
                "uploaded_at": photo.uploaded_at
            }
            for photo in waste_report.photos
        ] if waste_report.photos else [],
        user_email=waste_report.user.email if waste_report.user else None,
        user_username=waste_report.user.username if waste_report.user else None
    )
    
    return admin_response


@router.put("/{report_id}/status", response_model=WasteReportAdminResponse, operation_id="adminUpdateWasteReportStatus")
def update_waste_report_status(
    *,
    db: Session = Depends(get_db),
    report_id: int,
    status_update: WasteReportStatusUpdate,
    current_user: User = Depends(get_current_admin_user)
) -> Any:
    """
    Update waste report status and add admin notes.
    Admin only endpoint for approving, rejecting, or completing reports.
    """
    waste_report = WasteReportRepository.get_with_user(db=db, waste_report_id=report_id)
    if not waste_report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Waste report not found"
        )
    
    # Update status and admin notes
    updated_report = WasteReportRepository.update_status(
        db=db,
        db_waste_report=waste_report,
        status=status_update.status,
        admin_notes=status_update.admin_notes
    )
    
    # TODO: Send notification email to user about status change
    # email_service.send_status_change_notification(
    #     updated_report.user.email,
    #     updated_report,
    #     status_update.status
    # )
    
    # Return updated report with user information
    admin_response = WasteReportAdminResponse(
        id=updated_report.id,
        user_id=updated_report.user_id,
        street_address=updated_report.street_address,
        city=updated_report.city,
        postal_code=updated_report.postal_code,
        latitude=updated_report.latitude,
        longitude=updated_report.longitude,
        waste_type=updated_report.waste_type,
        quantity_estimate=updated_report.quantity_estimate,
        urgency_level=updated_report.urgency_level,
        description=updated_report.description,
        reporter_name=updated_report.reporter_name,
        reporter_phone=updated_report.reporter_phone,
        status=updated_report.status,
        admin_notes=updated_report.admin_notes,
        created_at=updated_report.created_at,
        updated_at=updated_report.updated_at,
        photos=[
            {
                "id": photo.id,
                "waste_report_id": photo.waste_report_id,
                "photo_url": photo.photo_url,
                "uploaded_at": photo.uploaded_at
            }
            for photo in updated_report.photos
        ] if updated_report.photos else [],
        user_email=updated_report.user.email if updated_report.user else None,
        user_username=updated_report.user.username if updated_report.user else None
    )
    
    return admin_response


@router.get("/stats/summary", operation_id="adminGetWasteReportStats")
def get_waste_report_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
    date_from: Optional[date] = Query(None, description="Filter from date (YYYY-MM-DD)"),
    date_to: Optional[date] = Query(None, description="Filter to date (YYYY-MM-DD)")
) -> Any:
    """
    Get waste report statistics for admin dashboard.
    Admin only endpoint.
    """
    # Get reports with filters
    all_reports, total = WasteReportRepository.get_multi_admin(
        db=db,
        skip=0,
        limit=10000,  # Get all reports for stats
        date_from=date_from,
        date_to=date_to
    )
    
    # Calculate statistics
    stats = {
        "total_reports": total,
        "status_breakdown": {
            "pending": 0,
            "approved": 0,
            "rejected": 0,
            "completed": 0
        },
        "waste_type_breakdown": {
            "household": 0,
            "recyclable": 0,
            "electronic": 0,
            "construction": 0,
            "hazardous": 0,
            "organic": 0,
            "illegal_dumping": 0,
            "other": 0
        },
        "urgency_breakdown": {
            "low": 0,
            "medium": 0,
            "high": 0,
            "critical": 0
        },
        "cities": {}
    }
    
    for report in all_reports:
        # Status breakdown
        stats["status_breakdown"][report.status.value] += 1
        
        # Waste type breakdown
        stats["waste_type_breakdown"][report.waste_type.value] += 1
        
        # Urgency breakdown
        stats["urgency_breakdown"][report.urgency_level.value] += 1
        
        # City breakdown
        city = report.city
        if city in stats["cities"]:
            stats["cities"][city] += 1
        else:
            stats["cities"][city] = 1
    
    # Sort cities by count (top 10)
    sorted_cities = sorted(stats["cities"].items(), key=lambda x: x[1], reverse=True)[:10]
    stats["top_cities"] = [{"city": city, "count": count} for city, count in sorted_cities]
    del stats["cities"]  # Remove the full cities dict to keep response clean
    
    return stats
