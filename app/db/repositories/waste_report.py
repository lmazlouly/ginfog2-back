from datetime import datetime
from typing import List, Optional, Union

from sqlalchemy.orm import Session

from app.db.models.waste_report import WasteReport
from app.schemas.waste_report import WasteReportCreate, WasteReportUpdate


class WasteReportRepository:
    @staticmethod
    def create(db: Session, *, waste_report_in: WasteReportCreate, user_id: int) -> WasteReport:
        """
        Create a new waste report
        """
        db_waste_report = WasteReport(
            location=waste_report_in.location,
            waste_type=waste_report_in.waste_type,
            quantity=waste_report_in.quantity,
            status=waste_report_in.status,
            user_id=user_id,
            date=datetime.now(datetime.timezone.utc),
        )
        db.add(db_waste_report)
        db.commit()
        db.refresh(db_waste_report)
        return db_waste_report

    @staticmethod
    def get(db: Session, waste_report_id: int) -> Optional[WasteReport]:
        """
        Get a waste report by ID
        """
        return db.query(WasteReport).filter(WasteReport.id == waste_report_id).first()

    @staticmethod
    def get_multi(
        db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[WasteReport]:
        """
        Get multiple waste reports
        """
        return db.query(WasteReport).offset(skip).limit(limit).all()

    @staticmethod
    def get_by_user_id(
        db: Session, *, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[WasteReport]:
        """
        Get waste reports for a specific user
        """
        return db.query(WasteReport).filter(
            WasteReport.user_id == user_id
        ).offset(skip).limit(limit).all()

    @staticmethod
    def update(
        db: Session, *, db_waste_report: WasteReport, waste_report_in: Union[WasteReportUpdate, dict]
    ) -> WasteReport:
        """
        Update a waste report
        """
        waste_report_data = db_waste_report.__dict__
        if isinstance(waste_report_in, dict):
            update_data = waste_report_in
        else:
            update_data = waste_report_in.model_dump(exclude_unset=True)
        for field in waste_report_data:
            if field in update_data:
                setattr(db_waste_report, field, update_data[field])
        db.add(db_waste_report)
        db.commit()
        db.refresh(db_waste_report)
        return db_waste_report

    @staticmethod
    def delete(db: Session, *, waste_report_id: int) -> bool:
        """
        Delete a waste report
        """
        waste_report = db.query(WasteReport).filter(WasteReport.id == waste_report_id).first()
        if not waste_report:
            return False
        db.delete(waste_report)
        db.commit()
        return True
