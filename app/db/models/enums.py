import enum


class WasteType(enum.Enum):
    HOUSEHOLD = "household"
    RECYCLABLE = "recyclable"
    ELECTRONIC = "electronic"
    CONSTRUCTION = "construction"
    HAZARDOUS = "hazardous"
    ORGANIC = "organic"
    ILLEGAL_DUMPING = "illegal_dumping"
    OTHER = "other"


class QuantityEstimate(enum.Enum):
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
    VERY_LARGE = "very_large"


class UrgencyLevel(enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ReportStatus(enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    COMPLETED = "completed"
