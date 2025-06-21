from datetime import datetime
from sqlalchemy import Column, DateTime, Enum, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import relationship

from app.db.session import Base
from app.db.models.enums import WasteType, QuantityEstimate, UrgencyLevel, ReportStatus


class WasteReport(Base):
    __tablename__ = "waste_reports"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Location information
    street_address = Column(String(255), nullable=False)
    city = Column(String(100), nullable=False)
    postal_code = Column(String(20), nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    
    # Waste information
    waste_type = Column(Enum(WasteType), nullable=False)
    quantity_estimate = Column(Enum(QuantityEstimate), nullable=False)
    urgency_level = Column(Enum(UrgencyLevel), nullable=False)
    description = Column(Text(1000), nullable=True)
    status = Column(Enum(ReportStatus), default=ReportStatus.PENDING, nullable=False)
    
    # Reporter information
    reporter_name = Column(String(100), nullable=False)
    reporter_phone = Column(String(20), nullable=True)
    
    # Admin fields
    admin_notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="waste_reports")
    photos = relationship("WastePhoto", back_populates="waste_report", cascade="all, delete-orphan")


class WastePhoto(Base):
    __tablename__ = "waste_photos"

    id = Column(Integer, primary_key=True, index=True)
    waste_report_id = Column(Integer, ForeignKey("waste_reports.id"), nullable=False)
    photo_url = Column(String(500), nullable=False)
    uploaded_at = Column(DateTime, default=func.now(), nullable=False)
    
    # Relationship
    waste_report = relationship("WasteReport", back_populates="photos")
