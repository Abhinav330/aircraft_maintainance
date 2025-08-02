from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Any
from datetime import datetime
from bson import ObjectId

class LogEntry(BaseModel):
    """Individual maintenance log entry"""
    description_of_work_performed: Optional[str] = None
    tach_time: Optional[str] = None
    hobbs_time: Optional[str] = None
    part_number_replaced: Optional[List[str]] = []
    manual_reference: Optional[str] = None
    reason_for_maintenance: Optional[str] = None
    ad_compliance: Optional[str] = None
    next_due_compliance: Optional[str] = None
    service_bulletin_reference: Optional[str] = None
    certification_statement: Optional[str] = None
    performed_by: Optional[str] = None
    license_number: Optional[str] = None
    date: Optional[str] = None
    risk_level: Optional[str] = None
    urgency: Optional[str] = None
    is_airworthy: Optional[bool] = True

    model_config = ConfigDict(
        json_encoders={ObjectId: str},
        json_schema_extra={
            "example": {
                "description_of_work_performed": "Replaced left main landing gear tire",
                "tach_time": "1250.5",
                "hobbs_time": "1250.5",
                "part_number_replaced": ["Tire-123", "Tube-456"],
                "manual_reference": "Aircraft Maintenance Manual Chapter 32",
                "reason_for_maintenance": "Scheduled maintenance",
                "ad_compliance": "AD 2023-15-02 complied with",
                "next_due_compliance": "Next inspection due in 50 hours",
                "service_bulletin_reference": "SB 2023-01",
                "certification_statement": "I certify that this aircraft is airworthy",
                "performed_by": "John Smith",
                "license_number": "A&P 123456",
                "date": "2024-01-15",
                "risk_level": "Low",
                "urgency": "Normal",
                "is_airworthy": True
            }
        }
    )

class MaintenanceLogData(BaseModel):
    """Structured data extracted from maintenance log image with multiple entries"""
    aircraft_registration: Optional[str] = None
    aircraft_make_model: Optional[str] = None
    summary: Optional[str] = None
    is_mult: Optional[bool] = False
    log_entries: List[LogEntry] = []

    model_config = ConfigDict(
        json_encoders={ObjectId: str},
        json_schema_extra={
            "example": {
                "aircraft_registration": "N123AB",
                "aircraft_make_model": "Cessna 172",
                "summary": "Multiple maintenance entries including tire replacement and engine inspection",
                "is_mult": True,
                "log_entries": [
                    {
                        "description_of_work_performed": "Replaced left main landing gear tire",
                        "tach_time": "1250.5",
                        "hobbs_time": "1250.5",
                        "part_number_replaced": ["Tire-123", "Tube-456"],
                        "manual_reference": "Aircraft Maintenance Manual Chapter 32",
                        "reason_for_maintenance": "Scheduled maintenance",
                        "ad_compliance": "AD 2023-15-02 complied with",
                        "next_due_compliance": "Next inspection due in 50 hours",
                        "service_bulletin_reference": "SB 2023-01",
                        "certification_statement": "I certify that this aircraft is airworthy",
                        "performed_by": "John Smith",
                        "license_number": "A&P 123456",
                        "date": "2024-01-15",
                        "risk_level": "Low",
                        "urgency": "Normal",
                        "is_airworthy": True
                    }
                ]
            }
        }
    )

class MaintenanceLog(BaseModel):
    """Complete maintenance log document"""
    id: Optional[str] = Field(default=None, alias="_id")
    uploaded_by: str = "anonymous"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    image_filename: Optional[str] = None
    structured_data: MaintenanceLogData
    original_image_url: Optional[str] = None

    model_config = ConfigDict(
        populate_by_name=True,
        json_encoders={ObjectId: str},
        json_schema_extra={
            "example": {
                "uploaded_by": "anonymous",
                "timestamp": "2024-01-15T10:30:00Z",
                "image_filename": "log_2024_01_15.jpg",
                "structured_data": {
                    "aircraft_registration": "N123AB",
                    "aircraft_make_model": "Cessna 172",
                    "summary": "Multiple maintenance entries including tire replacement and engine inspection",
                    "is_mult": True,
                    "log_entries": [
                        {
                            "description_of_work_performed": "Replaced left main landing gear tire",
                            "tach_time": "1250.5",
                            "hobbs_time": "1250.5",
                            "part_number_replaced": ["Tire-123", "Tube-456"],
                            "manual_reference": "Aircraft Maintenance Manual Chapter 32",
                            "reason_for_maintenance": "Scheduled maintenance",
                            "ad_compliance": "AD 2023-15-02 complied with",
                            "next_due_compliance": "Next inspection due in 50 hours",
                            "service_bulletin_reference": "SB 2023-01",
                            "certification_statement": "I certify that this aircraft is airworthy",
                            "performed_by": "John Smith",
                            "license_number": "A&P 123456",
                            "date": "2024-01-15",
                            "risk_level": "Low",
                            "urgency": "Normal",
                            "is_airworthy": True
                        }
                    ]
                }
            }
        }
    )

class LogSummary(BaseModel):
    """Summary view for sidebar history"""
    id: str = Field(alias="_id")
    aircraft_registration: Optional[str] = None
    timestamp: datetime
    description: Optional[str] = None
    risk_level: Optional[str] = None

    model_config = ConfigDict(
        populate_by_name=True,
        json_encoders={ObjectId: str}
    )

class UploadResponse(BaseModel):
    """Response model for upload endpoint"""
    success: bool
    message: str
    log_id: Optional[str] = None
    structured_data: Optional[MaintenanceLogData] = None

class ExportRequest(BaseModel):
    """Request model for export endpoint"""
    format: str = Field(..., description="Export format: 'json' or 'pdf'")
    log_id: str = Field(..., description="ID of the log to export") 