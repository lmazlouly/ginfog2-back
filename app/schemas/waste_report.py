from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class WasteReportStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    REJECTED = "rejected"


# Shared properties
class WasteReportBase(BaseModel):
    location: str
    waste_type: str
    quantity: float
    status: Optional[WasteReportStatus] = WasteReportStatus.PENDING


# Properties to receive on item creation
class WasteReportCreate(WasteReportBase):
    pass


# Properties to receive on item update
class WasteReportUpdate(BaseModel):
    location: Optional[str] = None
    waste_type: Optional[str] = None
    quantity: Optional[float] = None
    status: Optional[WasteReportStatus] = None


# Properties shared by models stored in DB
class WasteReportInDBBase(WasteReportBase):
    id: int
    user_id: int
    date: datetime
    
    class Config:
        from_attributes = True


# Properties to return to client
class WasteReport(WasteReportInDBBase):
    pass


# Properties stored in DB
class WasteReportInDB(WasteReportInDBBase):
    pass
