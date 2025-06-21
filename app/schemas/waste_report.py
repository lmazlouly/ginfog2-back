from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, validator

from app.db.models.enums import WasteType, QuantityEstimate, UrgencyLevel, ReportStatus


# Photo schemas
class WastePhotoBase(BaseModel):
    photo_url: str = Field(..., max_length=500)


class WastePhotoCreate(WastePhotoBase):
    pass


class WastePhotoResponse(WastePhotoBase):
    id: int
    waste_report_id: int
    uploaded_at: datetime
    
    class Config:
        from_attributes = True


# Waste Report schemas
class WasteReportBase(BaseModel):
    street_address: str = Field(..., max_length=255)
    city: str = Field(..., max_length=100)
    postal_code: str = Field(..., max_length=20)
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    waste_type: WasteType
    quantity_estimate: QuantityEstimate
    urgency_level: UrgencyLevel
    description: Optional[str] = Field(None, max_length=1000)
    reporter_name: str = Field(..., max_length=100)
    reporter_phone: Optional[str] = Field(None, max_length=20)


class WasteReportCreate(WasteReportBase):
    @validator('reporter_phone')
    def validate_phone(cls, v):
        if v and not v.replace('+', '').replace('-', '').replace(' ', '').replace('(', '').replace(')', '').isdigit():
            raise ValueError('Invalid phone number format')
        return v


class WasteReportUpdate(BaseModel):
    street_address: Optional[str] = Field(None, max_length=255)
    city: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    waste_type: Optional[WasteType] = None
    quantity_estimate: Optional[QuantityEstimate] = None
    urgency_level: Optional[UrgencyLevel] = None
    description: Optional[str] = Field(None, max_length=1000)
    reporter_name: Optional[str] = Field(None, max_length=100)
    reporter_phone: Optional[str] = Field(None, max_length=20)

    @validator('reporter_phone')
    def validate_phone(cls, v):
        if v and not v.replace('+', '').replace('-', '').replace(' ', '').replace('(', '').replace(')', '').isdigit():
            raise ValueError('Invalid phone number format')
        return v


class WasteReportResponse(WasteReportBase):
    id: int
    user_id: int
    status: ReportStatus
    admin_notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    photos: List[WastePhotoResponse] = []
    
    class Config:
        from_attributes = True


class WasteReportListItem(BaseModel):
    id: int
    street_address: str
    city: str
    waste_type: WasteType
    urgency_level: UrgencyLevel
    status: ReportStatus
    created_at: datetime
    photo_count: int = 0
    
    class Config:
        from_attributes = True


class WasteReportList(BaseModel):
    items: List[WasteReportListItem]
    total: int
    page: int
    size: int
    pages: int


# Admin schemas
class WasteReportStatusUpdate(BaseModel):
    status: ReportStatus
    admin_notes: Optional[str] = Field(None, max_length=2000)


class WasteReportAdminResponse(WasteReportResponse):
    user_email: Optional[str] = None
    user_username: Optional[str] = None


# Waste types endpoint schema
class WasteTypeInfo(BaseModel):
    value: str
    label: str
    description: str


class WasteTypesResponse(BaseModel):
    waste_types: List[WasteTypeInfo]
