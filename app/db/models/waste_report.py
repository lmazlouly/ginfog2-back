from datetime import datetime
from sqlalchemy import Column, DateTime, Enum, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.session import Base


class WasteReport(Base):
    __tablename__ = "waste_reports"

    id = Column(Integer, primary_key=True, index=True)
    location = Column(String(255), nullable=False)
    waste_type = Column(String(100), nullable=False)
    quantity = Column(Float, nullable=False)
    status = Column(
        Enum("pending", "processing", "completed", "rejected", name="waste_report_status"), 
        default="pending",
        nullable=False
    )
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(DateTime, default=datetime.utcnow(), nullable=False)
    
    # Relationship with user
    user = relationship("User", back_populates="waste_reports")
