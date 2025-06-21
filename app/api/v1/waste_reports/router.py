from datetime import date
from typing import Any, List, Optional
from math import ceil

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Query
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.dependencies import check_rate_limit, check_report_ownership, check_edit_permission, check_delete_permission
from app.core.file_upload import file_upload_service
from app.db.repositories.waste_report import WasteReportRepository, WastePhotoRepository
from app.db.session import get_db
from app.db.models.user import User
from app.db.models.enums import WasteType, ReportStatus, UrgencyLevel
from app.schemas.waste_report import (
    WasteReportCreate, WasteReportUpdate, WasteReportResponse, 
    WasteReportList, WasteReportListItem, WasteTypesResponse, WasteTypeInfo
)

router = APIRouter(prefix="/waste-reports", tags=["waste-reports"])


@router.post("", response_model=WasteReportResponse, operation_id="createWasteReport")
async def create_waste_report(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_rate_limit),  # Rate limiting applied here
    # Form data for the waste report
    street_address: str = Form(..., max_length=255),
    city: str = Form(..., max_length=100),
    postal_code: str = Form(..., max_length=20),
    latitude: Optional[float] = Form(None),
    longitude: Optional[float] = Form(None),
    waste_type: WasteType = Form(...),
    quantity_estimate: str = Form(...),
    urgency_level: UrgencyLevel = Form(...),
    description: Optional[str] = Form(None, max_length=1000),
    reporter_name: str = Form(..., max_length=100),
    reporter_phone: Optional[str] = Form(None, max_length=20),
    # File uploads
    photos: List[UploadFile] = File(default=[])
) -> Any:
    """
    Create a new waste report with optional photo uploads.
    Rate limited to 10 reports per day per user.
    """
    try:
        # Create the waste report data object
        waste_report_data = WasteReportCreate(
            street_address=street_address,
            city=city,
            postal_code=postal_code,
            latitude=latitude,
            longitude=longitude,
            waste_type=waste_type,
            quantity_estimate=quantity_estimate,
            urgency_level=urgency_level,
            description=description,
            reporter_name=reporter_name,
            reporter_phone=reporter_phone
        )
        
        # Create the waste report
        waste_report = WasteReportRepository.create(
            db=db, waste_report_in=waste_report_data, user_id=current_user.id
        )
        
        # Handle photo uploads if any
        if photos and any(photo.filename for photo in photos):
            try:
                photo_urls = await file_upload_service.save_multiple_files(photos, waste_report.id)
                
                # Save photo records to database
                if photo_urls:
                    WastePhotoRepository.create_multiple(
                        db=db, waste_report_id=waste_report.id, photo_urls=photo_urls
                    )
            except Exception as e:
                # If photo upload fails, still return the report but log the error
                # In production, you might want to handle this differently
                pass
        
        # Refresh to get the report with photos
        waste_report = WasteReportRepository.get(db=db, waste_report_id=waste_report.id)
        
        # TODO: Send confirmation email to user
        # email_service.send_report_confirmation(current_user.email, waste_report)
        
        return waste_report
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create waste report"
        )


@router.get("", response_model=WasteReportList, operation_id="getWasteReports")
def get_waste_reports(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Items per page"),
    status: Optional[ReportStatus] = Query(None, description="Filter by status"),
    waste_type: Optional[WasteType] = Query(None, description="Filter by waste type"),
    date_from: Optional[date] = Query(None, description="Filter from date (YYYY-MM-DD)"),
    date_to: Optional[date] = Query(None, description="Filter to date (YYYY-MM-DD)"),
    sort_by: str = Query("created_at", description="Sort by field"),
    sort_order: str = Query("desc", regex="^(asc|desc)$", description="Sort order")
) -> Any:
    """
    Get user's waste reports with filtering, pagination, and sorting.
    """
    skip = (page - 1) * size
    
    items, total = WasteReportRepository.get_multi_by_user(
        db=db,
        user_id=current_user.id,
        skip=skip,
        limit=size,
        status=status,
        waste_type=waste_type,
        date_from=date_from,
        date_to=date_to,
        sort_by=sort_by,
        sort_order=sort_order
    )
    
    # Convert to list items with photo count
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


@router.get("/{report_id}", response_model=WasteReportResponse, operation_id="getWasteReport")
def get_waste_report(
    *,
    db: Session = Depends(get_db),
    report_id: int,
    current_user: User = Depends(check_report_ownership)
) -> Any:
    """
    Get a specific waste report by ID.
    Users can only access their own reports unless they are admin.
    """
    waste_report = WasteReportRepository.get(db=db, waste_report_id=report_id)
    if not waste_report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Waste report not found"
        )
    
    return waste_report


@router.put("/{report_id}", response_model=WasteReportResponse, operation_id="updateWasteReport")
async def update_waste_report(
    *,
    db: Session = Depends(get_db),
    report_id: int,
    current_user: User = Depends(check_edit_permission),
    # Form data for updates
    street_address: Optional[str] = Form(None, max_length=255),
    city: Optional[str] = Form(None, max_length=100),
    postal_code: Optional[str] = Form(None, max_length=20),
    latitude: Optional[float] = Form(None),
    longitude: Optional[float] = Form(None),
    waste_type: Optional[WasteType] = Form(None),
    quantity_estimate: Optional[str] = Form(None),
    urgency_level: Optional[UrgencyLevel] = Form(None),
    description: Optional[str] = Form(None, max_length=1000),
    reporter_name: Optional[str] = Form(None, max_length=100),
    reporter_phone: Optional[str] = Form(None, max_length=20),
    # File uploads
    photos: List[UploadFile] = File(default=[])
) -> Any:
    """
    Update a waste report.
    Users can only edit their own pending reports unless they are admin.
    """
    waste_report = WasteReportRepository.get(db=db, waste_report_id=report_id)
    if not waste_report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Waste report not found"
        )
    
    # Create update data from provided fields
    update_data = {}
    if street_address is not None:
        update_data["street_address"] = street_address
    if city is not None:
        update_data["city"] = city
    if postal_code is not None:
        update_data["postal_code"] = postal_code
    if latitude is not None:
        update_data["latitude"] = latitude
    if longitude is not None:
        update_data["longitude"] = longitude
    if waste_type is not None:
        update_data["waste_type"] = waste_type
    if quantity_estimate is not None:
        update_data["quantity_estimate"] = quantity_estimate
    if urgency_level is not None:
        update_data["urgency_level"] = urgency_level
    if description is not None:
        update_data["description"] = description
    if reporter_name is not None:
        update_data["reporter_name"] = reporter_name
    if reporter_phone is not None:
        update_data["reporter_phone"] = reporter_phone
    
    # Update the waste report
    if update_data:
        waste_report = WasteReportRepository.update(
            db=db, db_waste_report=waste_report, waste_report_in=update_data
        )
    
    # Handle new photo uploads if any
    if photos and any(photo.filename for photo in photos):
        try:
            photo_urls = await file_upload_service.save_multiple_files(photos, waste_report.id)
            
            # Save photo records to database
            if photo_urls:
                WastePhotoRepository.create_multiple(
                    db=db, waste_report_id=waste_report.id, photo_urls=photo_urls
                )
        except Exception as e:
            # If photo upload fails, continue with the update
            pass
    
    # Refresh to get updated report with photos
    waste_report = WasteReportRepository.get(db=db, waste_report_id=report_id)
    return waste_report


@router.delete("/{report_id}", operation_id="deleteWasteReport")
def delete_waste_report(
    *,
    db: Session = Depends(get_db),
    report_id: int,
    current_user: User = Depends(check_delete_permission)
) -> Any:
    """
    Delete a waste report.
    Users can only delete their own pending reports unless they are admin.
    """
    waste_report = WasteReportRepository.get(db=db, waste_report_id=report_id)
    if not waste_report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Waste report not found"
        )
    
    # Delete associated files
    file_upload_service.delete_report_files(report_id)
    
    # Delete the report (photos will be cascade deleted)
    success = WasteReportRepository.delete(db=db, waste_report_id=report_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete waste report"
        )
    
    return {"message": "Waste report deleted successfully"}


@router.get("/types", response_model=WasteTypesResponse, operation_id="getWasteTypes")
def get_waste_types() -> Any:
    """
    Get available waste types with descriptions.
    Public endpoint - no authentication required.
    """
    waste_types = [
        WasteTypeInfo(
            value=WasteType.HOUSEHOLD.value,
            label="Household Waste",
            description="General household garbage and non-recyclable items"
        ),
        WasteTypeInfo(
            value=WasteType.RECYCLABLE.value,
            label="Recyclable Materials",
            description="Paper, plastic, glass, metal that can be recycled"
        ),
        WasteTypeInfo(
            value=WasteType.ELECTRONIC.value,
            label="Electronic Waste",
            description="Computers, phones, batteries, and electronic devices"
        ),
        WasteTypeInfo(
            value=WasteType.CONSTRUCTION.value,
            label="Construction Debris",
            description="Building materials, concrete, wood, drywall"
        ),
        WasteTypeInfo(
            value=WasteType.HAZARDOUS.value,
            label="Hazardous Materials",
            description="Chemicals, paints, oils, and dangerous substances"
        ),
        WasteTypeInfo(
            value=WasteType.ORGANIC.value,
            label="Organic Waste",
            description="Food scraps, yard waste, compostable materials"
        ),
        WasteTypeInfo(
            value=WasteType.ILLEGAL_DUMPING.value,
            label="Illegal Dumping",
            description="Unauthorized disposal of waste in public areas"
        ),
        WasteTypeInfo(
            value=WasteType.OTHER.value,
            label="Other",
            description="Other types of waste not listed above"
        )
    ]
    
    return WasteTypesResponse(waste_types=waste_types)
