from datetime import datetime, date
from typing import List, Optional, Union, Dict, Any
from sqlalchemy import and_, or_, desc, asc, func
from sqlalchemy.orm import Session, joinedload

from app.db.models.waste_report import WasteReport, WastePhoto
from app.db.models.user import User
from app.db.models.enums import WasteType, ReportStatus, UrgencyLevel
from app.schemas.waste_report import WasteReportCreate, WasteReportUpdate


class WasteReportRepository:
    @staticmethod
    def create(db: Session, *, waste_report_in: WasteReportCreate, user_id: int) -> WasteReport:
        """Create a new waste report"""
        db_waste_report = WasteReport(
            user_id=user_id,
            street_address=waste_report_in.street_address,
            city=waste_report_in.city,
            postal_code=waste_report_in.postal_code,
            latitude=waste_report_in.latitude,
            longitude=waste_report_in.longitude,
            waste_type=waste_report_in.waste_type,
            quantity_estimate=waste_report_in.quantity_estimate,
            urgency_level=waste_report_in.urgency_level,
            description=waste_report_in.description,
            reporter_name=waste_report_in.reporter_name,
            reporter_phone=waste_report_in.reporter_phone,
        )
        db.add(db_waste_report)
        db.commit()
        db.refresh(db_waste_report)
        return db_waste_report

    @staticmethod
    def get(db: Session, waste_report_id: int) -> Optional[WasteReport]:
        """Get a waste report by ID with photos"""
        return db.query(WasteReport).options(
            joinedload(WasteReport.photos)
        ).filter(WasteReport.id == waste_report_id).first()

    @staticmethod
    def get_with_user(db: Session, waste_report_id: int) -> Optional[WasteReport]:
        """Get a waste report by ID with user and photos (for admin)"""
        return db.query(WasteReport).options(
            joinedload(WasteReport.user),
            joinedload(WasteReport.photos)
        ).filter(WasteReport.id == waste_report_id).first()

    @staticmethod
    def get_multi_by_user(
        db: Session,
        *,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
        status: Optional[ReportStatus] = None,
        waste_type: Optional[WasteType] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc"
    ) -> tuple[List[WasteReport], int]:
        """Get waste reports for a specific user with filtering and pagination"""
        
        query = db.query(WasteReport).filter(WasteReport.user_id == user_id)
        
        # Apply filters
        if status:
            query = query.filter(WasteReport.status == status)
        if waste_type:
            query = query.filter(WasteReport.waste_type == waste_type)
        if date_from:
            query = query.filter(WasteReport.created_at >= date_from)
        if date_to:
            query = query.filter(WasteReport.created_at <= date_to)
        
        # Get total count before pagination
        total = query.count()
        
        # Apply sorting
        sort_column = getattr(WasteReport, sort_by, WasteReport.created_at)
        if sort_order.lower() == "desc":
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(asc(sort_column))
        
        # Apply pagination
        items = query.offset(skip).limit(limit).all()
        
        return items, total

    @staticmethod
    def get_multi_admin(
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        status: Optional[ReportStatus] = None,
        waste_type: Optional[WasteType] = None,
        urgency_level: Optional[UrgencyLevel] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        city: Optional[str] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc"
    ) -> tuple[List[WasteReport], int]:
        """Get all waste reports for admin with advanced filtering"""
        
        query = db.query(WasteReport).options(joinedload(WasteReport.user))
        
        # Apply filters
        if status:
            query = query.filter(WasteReport.status == status)
        if waste_type:
            query = query.filter(WasteReport.waste_type == waste_type)
        if urgency_level:
            query = query.filter(WasteReport.urgency_level == urgency_level)
        if date_from:
            query = query.filter(WasteReport.created_at >= date_from)
        if date_to:
            query = query.filter(WasteReport.created_at <= date_to)
        if city:
            query = query.filter(WasteReport.city.ilike(f"%{city}%"))
        
        # Get total count before pagination
        total = query.count()
        
        # Apply sorting
        sort_column = getattr(WasteReport, sort_by, WasteReport.created_at)
        if sort_order.lower() == "desc":
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(asc(sort_column))
        
        # Apply pagination
        items = query.offset(skip).limit(limit).all()
        
        return items, total

    @staticmethod
    def update(
        db: Session, *, db_waste_report: WasteReport, waste_report_in: Union[WasteReportUpdate, dict]
    ) -> WasteReport:
        """Update a waste report"""
        if isinstance(waste_report_in, dict):
            update_data = waste_report_in
        else:
            update_data = waste_report_in.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            if hasattr(db_waste_report, field):
                setattr(db_waste_report, field, value)
        
        db.add(db_waste_report)
        db.commit()
        db.refresh(db_waste_report)
        return db_waste_report

    @staticmethod
    def update_status(
        db: Session, *, db_waste_report: WasteReport, status: ReportStatus, admin_notes: Optional[str] = None
    ) -> WasteReport:
        """Update waste report status and admin notes"""
        db_waste_report.status = status
        if admin_notes is not None:
            db_waste_report.admin_notes = admin_notes
        
        db.add(db_waste_report)
        db.commit()
        db.refresh(db_waste_report)
        return db_waste_report

    @staticmethod
    def delete(db: Session, *, waste_report_id: int) -> bool:
        """Delete a waste report"""
        waste_report = db.query(WasteReport).filter(WasteReport.id == waste_report_id).first()
        if not waste_report:
            return False
        db.delete(waste_report)
        db.commit()
        return True

    @staticmethod
    def count_user_reports_today(db: Session, user_id: int) -> int:
        """Count reports created by user today (for rate limiting)"""
        today = date.today()
        return db.query(WasteReport).filter(
            and_(
                WasteReport.user_id == user_id,
                func.date(WasteReport.created_at) == today
            )
        ).count()

    @staticmethod
    def can_user_edit(db: Session, report_id: int, user_id: int) -> bool:
        """Check if user can edit the report (own report and pending status)"""
        report = db.query(WasteReport).filter(
            and_(
                WasteReport.id == report_id,
                WasteReport.user_id == user_id,
                WasteReport.status == ReportStatus.PENDING
            )
        ).first()
        return report is not None

    @staticmethod
    def can_user_delete(db: Session, report_id: int, user_id: int) -> bool:
        """Check if user can delete the report (own report and pending status)"""
        return WasteReportRepository.can_user_edit(db, report_id, user_id)


class WastePhotoRepository:
    @staticmethod
    def create(db: Session, *, waste_report_id: int, photo_url: str) -> WastePhoto:
        """Create a new waste photo"""
        db_photo = WastePhoto(
            waste_report_id=waste_report_id,
            photo_url=photo_url
        )
        db.add(db_photo)
        db.commit()
        db.refresh(db_photo)
        return db_photo

    @staticmethod
    def create_multiple(db: Session, *, waste_report_id: int, photo_urls: List[str]) -> List[WastePhoto]:
        """Create multiple waste photos"""
        photos = []
        for photo_url in photo_urls:
            db_photo = WastePhoto(
                waste_report_id=waste_report_id,
                photo_url=photo_url
            )
            photos.append(db_photo)
        
        db.add_all(photos)
        db.commit()
        for photo in photos:
            db.refresh(photo)
        return photos

    @staticmethod
    def get_by_report_id(db: Session, waste_report_id: int) -> List[WastePhoto]:
        """Get all photos for a waste report"""
        return db.query(WastePhoto).filter(
            WastePhoto.waste_report_id == waste_report_id
        ).all()

    @staticmethod
    def delete_by_report_id(db: Session, waste_report_id: int) -> bool:
        """Delete all photos for a waste report"""
        photos = db.query(WastePhoto).filter(
            WastePhoto.waste_report_id == waste_report_id
        ).all()
        
        for photo in photos:
            db.delete(photo)
        
        db.commit()
        return True

    @staticmethod
    def delete(db: Session, photo_id: int) -> bool:
        """Delete a specific photo"""
        photo = db.query(WastePhoto).filter(WastePhoto.id == photo_id).first()
        if not photo:
            return False
        db.delete(photo)
        db.commit()
        return True
