from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_active_user, get_current_user
from app.db.repositories.waste_report import WasteReportRepository
from app.db.session import get_db
from app.schemas.user import User
from app.schemas.waste_report import WasteReport, WasteReportCreate, WasteReportUpdate

router = APIRouter(prefix="/waste-reports", tags=["waste-reports"])


@router.post("", response_model=WasteReport, operation_id="createWasteReport")
def create_waste_report(
    *,
    db: Session = Depends(get_db),
    waste_report_in: WasteReportCreate,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Create a new waste report
    """
    waste_report = WasteReportRepository.create(
        db=db, waste_report_in=waste_report_in, user_id=current_user.id
    )
    return waste_report


@router.get("", response_model=List[WasteReport], operation_id="getWasteReports")
def read_waste_reports(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Retrieve waste reports.
    Regular users get only their reports, superusers get all reports.
    """
    if current_user.is_superuser:
        waste_reports = WasteReportRepository.get_multi(db, skip=skip, limit=limit)
    else:
        waste_reports = WasteReportRepository.get_by_user_id(
            db=db, user_id=current_user.id, skip=skip, limit=limit
        )
    return waste_reports


@router.get("/{waste_report_id}", response_model=WasteReport, operation_id="getWasteReport")
def read_waste_report(
    *,
    db: Session = Depends(get_db),
    waste_report_id: int,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Get waste report by ID.
    Regular users can only access their own reports, superusers can access any report.
    """
    waste_report = WasteReportRepository.get(db=db, waste_report_id=waste_report_id)
    if not waste_report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Waste report not found",
        )
    if not current_user.is_superuser and (waste_report.user_id != current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    return waste_report


@router.put("/{waste_report_id}", response_model=WasteReport, operation_id="updateWasteReport")
def update_waste_report(
    *,
    db: Session = Depends(get_db),
    waste_report_id: int,
    waste_report_in: WasteReportUpdate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Update a waste report.
    Regular users can only update their own reports, superusers can update any report.
    """
    waste_report = WasteReportRepository.get(db=db, waste_report_id=waste_report_id)
    if not waste_report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Waste report not found",
        )
    if not current_user.is_superuser and (waste_report.user_id != current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    waste_report = WasteReportRepository.update(
        db=db, db_waste_report=waste_report, waste_report_in=waste_report_in
    )
    return waste_report


@router.delete("/{waste_report_id}", operation_id="deleteWasteReport")
def delete_waste_report(
    *,
    db: Session = Depends(get_db),
    waste_report_id: int,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Delete a waste report.
    Regular users can only delete their own reports, superusers can delete any report.
    """
    waste_report = WasteReportRepository.get(db=db, waste_report_id=waste_report_id)
    if not waste_report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Waste report not found",
        )
    if not current_user.is_superuser and (waste_report.user_id != current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    WasteReportRepository.delete(db=db, waste_report_id=waste_report_id)
    return {"success": True}
