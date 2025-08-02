import os
import logging
from typing import List
from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from fastapi.responses import JSONResponse, FileResponse, StreamingResponse
from datetime import datetime
import json
from bson import ObjectId
import shutil
from pathlib import Path
from urllib.parse import unquote
from datetime import datetime
from io import BytesIO
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

from models import MaintenanceLog, MaintenanceLogData, LogSummary, UploadResponse, ExportRequest
from database import Database
from ai_service import AIService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["maintenance-logs"])

# Initialize AI service lazily
_ai_service = None

def get_ai_service():
    """Get or create AI service instance"""
    global _ai_service
    if _ai_service is None:
        print(f"🔄 Initializing AI service...")
        _ai_service = AIService()
        print(f"✅ AI service initialized")
    return _ai_service

@router.post("/upload-log/", response_model=UploadResponse)
async def upload_maintenance_log(file: UploadFile = File(...)):
    """
    Upload and analyze a maintenance log image using AI
    """
    print(f"=== UPLOAD START === File: {file.filename}, Content-Type: {file.content_type}")
    try:
        # Validate file type
        if not file.content_type.startswith('image/'):
            print(f"❌ Invalid file type: {file.content_type}")
            raise HTTPException(status_code=400, detail="File must be an image")
        
        print(f"✅ File type validation passed")
        
        # Read image bytes
        image_bytes = await file.read()
        print(f"✅ Image bytes read: {len(image_bytes)} bytes")
        
        # Save image file
        print(f"🔄 Saving image file")
        uploads_dir = Path("uploads")
        print(f"📝 Uploads directory path: {uploads_dir.absolute()}")
        uploads_dir.mkdir(exist_ok=True)
        print(f"✅ Uploads directory created/verified")
        
        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_extension = Path(file.filename).suffix if file.filename else ".jpg"
        image_filename = f"maintenance_log_{timestamp}{file_extension}"
        image_path = uploads_dir / image_filename
        print(f"📝 Generated filename: {image_filename}")
        print(f"📝 Full image path: {image_path.absolute()}")
        
        # Save the image
        try:
            with open(image_path, "wb") as f:
                f.write(image_bytes)
            print(f"✅ Image saved successfully to: {image_path.absolute()}")
            print(f"📝 File size: {image_path.stat().st_size} bytes")
        except Exception as e:
            print(f"❌ ERROR saving image: {e}")
            raise e
        
        # Analyze image with AI
        print(f"🔄 Starting AI analysis for: {file.filename}")
        logger.info(f"Analyzing maintenance log image: {file.filename}")
        structured_data = await get_ai_service().analyze_maintenance_log(image_bytes)
        print(f"✅ AI analysis completed. Structured data keys: {list(structured_data.keys())}")
        
        # Create maintenance log data model
        print(f"🔄 Creating MaintenanceLogData model")
        log_data = MaintenanceLogData(**structured_data)
        print(f"✅ MaintenanceLogData created successfully")
        
        # Create maintenance log document
        print(f"🔄 Creating MaintenanceLog document")
        maintenance_log = MaintenanceLog(
            image_filename=image_filename,
            structured_data=log_data
        )
        print(f"✅ MaintenanceLog document created")
        
        # Save to database
        print(f"🔄 Preparing database insertion")
        collection = Database.get_collection()
        print(f"✅ Database collection obtained")
        
        log_dict = maintenance_log.dict(by_alias=True, exclude={'id'})
        print(f"📝 Log dict prepared: {list(log_dict.keys())}")
        print(f"📝 Log dict _id field: {log_dict.get('_id', 'NOT PRESENT')}")
        
        result = await collection.insert_one(log_dict)
        print(f"✅ Database insertion completed")
        print(f"📝 Insert result: {result}")
        print(f"📝 Inserted ID: {result.inserted_id}")
        print(f"📝 Inserted ID type: {type(result.inserted_id)}")
        
        # Get the inserted document ID
        log_id = str(result.inserted_id)
        print(f"✅ Log ID converted to string: {log_id}")
        
        logger.info(f"Successfully saved maintenance log with ID: {log_id}")
        print(f"✅ Successfully saved maintenance log with ID: {log_id}")
        
        response = UploadResponse(
            success=True,
            message="Maintenance log analyzed and saved successfully",
            log_id=log_id,
            structured_data=log_data
        )
        print(f"✅ UploadResponse created: {response}")
        print(f"📝 Response data:")
        print(f"   - Success: {response.success}")
        print(f"   - Message: {response.message}")
        print(f"   - Log ID: {response.log_id}")
        print(f"   - Structured data keys: {list(response.structured_data.dict().keys()) if response.structured_data else 'None'}")
        if response.structured_data:
            print(f"   - Aircraft registration: {response.structured_data.aircraft_registration}")
            print(f"   - Aircraft make/model: {response.structured_data.aircraft_make_model}")
            print(f"   - Summary: {response.structured_data.summary}")
            print(f"   - Is multiple entries: {response.structured_data.is_mult}")
            print(f"   - Number of log entries: {len(response.structured_data.log_entries)}")
        
        return response
        
    except Exception as e:
        print(f"❌ ERROR in upload_maintenance_log: {e}")
        print(f"❌ ERROR type: {type(e)}")
        import traceback
        print(f"❌ ERROR traceback: {traceback.format_exc()}")
        logger.error(f"Error uploading maintenance log: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process maintenance log: {str(e)}")

@router.get("/logs/", response_model=List[LogSummary])
async def get_all_logs():
    """
    Get all maintenance logs (summary view for sidebar)
    """
    print(f"=== GET ALL LOGS START ===")
    try:
        collection = Database.get_collection()
        print(f"✅ Database collection obtained")
        
        cursor = collection.find({}).sort("timestamp", -1).limit(50)
        print(f"✅ Database cursor created")
        
        logs = []
        async for doc in cursor:
            print(f"📝 Processing document: {doc.get('_id', 'NO_ID')}")
            
            # Extract aircraft registration from structured data
            structured_data = doc.get("structured_data", {})
            aircraft_reg = structured_data.get("aircraft_registration", "Unknown")
            
            # Get description and check if it's multiple entries
            description = ""
            risk_level = None
            log_entries = structured_data.get("log_entries", [])
            is_mult = structured_data.get("is_mult", False)
            summary = structured_data.get("summary", "")
            
            if log_entries and len(log_entries) > 0:
                # Use the first entry's description
                first_entry = log_entries[0]
                description = first_entry.get("description_of_work_performed", "")
                risk_level = first_entry.get("risk_level")
                
                # If multiple entries and we have a summary, use it
                if is_mult and summary:
                    description = summary
                # If multiple entries but no summary, add count to description
                elif len(log_entries) > 1:
                    description += f" (+{len(log_entries) - 1} more entries)"
            else:
                # Fallback to old structure
                description = structured_data.get("description_of_work_performed", "")
                risk_level = structured_data.get("risk_level")
            
            print(f"📝 Aircraft reg: {aircraft_reg}, Description: {description[:50] if description else 'None'}...")
            
            log_summary = LogSummary(
                id=str(doc["_id"]),  # Convert ObjectId to string
                aircraft_registration=aircraft_reg,
                timestamp=doc["timestamp"],
                description=description[:100] + "..." if description and len(description) > 100 else (description or "No description"),
                risk_level=risk_level
            )
            logs.append(log_summary)
            print(f"✅ LogSummary created for ID: {str(doc['_id'])}")
        
        print(f"✅ Total logs retrieved: {len(logs)}")
        print(f"📝 Response data:")
        print(f"   - Number of logs: {len(logs)}")
        for i, log in enumerate(logs):
            print(f"   - Log {i+1}:")
            print(f"     * ID: {log.id}")
            print(f"     * Aircraft: {log.aircraft_registration}")
            print(f"     * Description: {log.description[:50] if log.description else 'None'}...")
            print(f"     * Risk Level: {log.risk_level}")
            print(f"     * Timestamp: {log.timestamp}")
        
        return logs
        
    except Exception as e:
        print(f"❌ ERROR in get_all_logs: {e}")
        import traceback
        print(f"❌ ERROR traceback: {traceback.format_exc()}")
        logger.error(f"Error retrieving logs: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve logs: {str(e)}")

@router.get("/logs/{log_id}", response_model=MaintenanceLog)
async def get_log_by_id(log_id: str):
    """
    Get full structured data for one maintenance log
    """
    print(f"=== GET LOG BY ID START === Log ID: {log_id}")
    try:
        # Validate ObjectId
        print(f"🔄 Validating ObjectId: {log_id}")
        if not ObjectId.is_valid(log_id):
            print(f"❌ Invalid ObjectId format: {log_id}")
            raise HTTPException(status_code=400, detail="Invalid log ID format")
        
        print(f"✅ ObjectId validation passed")
        
        collection = Database.get_collection()
        print(f"✅ Database collection obtained")
        
        print(f"🔄 Searching for document with _id: {ObjectId(log_id)}")
        doc = await collection.find_one({"_id": ObjectId(log_id)})
        
        if not doc:
            print(f"❌ Document not found for ID: {log_id}")
            raise HTTPException(status_code=404, detail="Maintenance log not found")
        
        print(f"✅ Document found: {doc.get('_id', 'NO_ID')}")
        print(f"📝 Document keys: {list(doc.keys())}")
        
        # Convert the _id to string for proper Pydantic validation
        original_id = doc["_id"]
        doc["_id"] = str(doc["_id"])
        print(f"📝 Converted _id from {original_id} to {doc['_id']}")
        
        print(f"🔄 Creating MaintenanceLog from document")
        maintenance_log = MaintenanceLog(**doc)
        print(f"✅ MaintenanceLog created successfully")
        print(f"📝 Response data:")
        print(f"   - Log ID: {maintenance_log.id}")
        print(f"   - Image filename: {maintenance_log.image_filename}")
        print(f"   - Uploaded by: {maintenance_log.uploaded_by}")
        print(f"   - Timestamp: {maintenance_log.timestamp}")
        if maintenance_log.structured_data:
            print(f"   - Aircraft registration: {maintenance_log.structured_data.aircraft_registration}")
            print(f"   - Aircraft make/model: {maintenance_log.structured_data.aircraft_make_model}")
            print(f"   - Summary: {maintenance_log.structured_data.summary}")
            print(f"   - Is multiple entries: {maintenance_log.structured_data.is_mult}")
            print(f"   - Number of log entries: {len(maintenance_log.structured_data.log_entries)}")
        
        return maintenance_log
        
    except HTTPException:
        print(f"❌ HTTPException raised, re-raising")
        raise
    except Exception as e:
        print(f"❌ ERROR in get_log_by_id: {e}")
        import traceback
        print(f"❌ ERROR traceback: {traceback.format_exc()}")
        logger.error(f"Error retrieving log {log_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve log: {str(e)}")

@router.put("/logs/{log_id}", response_model=MaintenanceLog)
async def update_log(log_id: str, log_data: MaintenanceLogData):
    """
    Update a maintenance log
    """
    print(f"=== UPDATE LOG START === Log ID: {log_id}")
    try:
        # Validate ObjectId
        if not ObjectId.is_valid(log_id):
            raise HTTPException(status_code=400, detail="Invalid log ID format")
        
        collection = Database.get_collection()
        
        # Update the document
        result = await collection.update_one(
            {"_id": ObjectId(log_id)},
            {"$set": {"structured_data": log_data.dict()}}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Maintenance log not found")
        
        # Return the updated document
        updated_doc = await collection.find_one({"_id": ObjectId(log_id)})
        # Convert the _id to string for proper Pydantic validation
        updated_doc["_id"] = str(updated_doc["_id"])
        maintenance_log = MaintenanceLog(**updated_doc)
        print(f"✅ Update completed successfully")
        print(f"📝 Response data:")
        print(f"   - Log ID: {maintenance_log.id}")
        print(f"   - Matched count: {result.matched_count}")
        print(f"   - Modified count: {result.modified_count}")
        if maintenance_log.structured_data:
            print(f"   - Aircraft registration: {maintenance_log.structured_data.aircraft_registration}")
            print(f"   - Aircraft make/model: {maintenance_log.structured_data.aircraft_make_model}")
            print(f"   - Summary: {maintenance_log.structured_data.summary}")
            print(f"   - Is multiple entries: {maintenance_log.structured_data.is_mult}")
            print(f"   - Number of log entries: {len(maintenance_log.structured_data.log_entries)}")
        
        return maintenance_log
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating log {log_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update log: {str(e)}")

def generate_maintenance_log_pdf(log_data):
    """
    Generate a modern, compact PDF report for a maintenance log with multiple entries
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=0.5*inch, rightMargin=0.5*inch, topMargin=0.5*inch, bottomMargin=0.5*inch)
    story = []
    
    # Helper function to safely get string values
    def safe_str(value, default="Not specified"):
        if value is None:
            return default
        return str(value)
    
    # Get styles
    styles = getSampleStyleSheet()
    
    # Modern color scheme
    primary_color = colors.HexColor('#1e40af')  # Blue
    secondary_color = colors.HexColor('#64748b')  # Gray
    accent_color = colors.HexColor('#f59e0b')  # Amber
    success_color = colors.HexColor('#059669')  # Green
    danger_color = colors.HexColor('#dc2626')  # Red
    
    # Custom styles
    title_style = ParagraphStyle(
        'ModernTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=20,
        alignment=TA_CENTER,
        textColor=primary_color,
        fontName='Helvetica-Bold'
    )
    
    section_style = ParagraphStyle(
        'SectionTitle',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=8,
        spaceBefore=15,
        textColor=primary_color,
        fontName='Helvetica-Bold'
    )
    
    entry_style = ParagraphStyle(
        'EntryTitle',
        parent=styles['Heading3'],
        fontSize=12,
        spaceAfter=6,
        spaceBefore=10,
        textColor=colors.HexColor('#7c3aed'),
        fontName='Helvetica-Bold'
    )
    
    label_style = ParagraphStyle(
        'Label',
        parent=styles['Normal'],
        fontSize=10,
        textColor=secondary_color,
        fontName='Helvetica-Bold'
    )
    
    value_style = ParagraphStyle(
        'Value',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.black,
        fontName='Helvetica'
    )
    
    normal_style = ParagraphStyle(
        'Normal',
        parent=styles['Normal'],
        fontSize=10,
        fontName='Helvetica'
    )
    
    # Header with logo-like design
    header_data = [
        [Paragraph("✈️ AIRCRAFT MAINTENANCE LOG", title_style)]
    ]
    header_table = Table(header_data, colWidths=[7*inch])
    header_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
        ('ROUNDEDCORNERS', (0, 0), (-1, -1), 10),
        ('LEFTPADDING', (0, 0), (-1, -1), 20),
        ('RIGHTPADDING', (0, 0), (-1, -1), 20),
        ('TOPPADDING', (0, 0), (-1, -1), 15),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 15))
    
    # Get structured data safely
    structured_data = log_data.get("structured_data", {})
    log_entries = structured_data.get("log_entries", [])
    
    # Aircraft Information - Compact 2-column layout
    aircraft_info = [
        [
            Paragraph("Aircraft Registration", label_style),
            Paragraph(safe_str(structured_data.get("aircraft_registration")), value_style)
        ],
        [
            Paragraph("Make/Model", label_style),
            Paragraph(safe_str(structured_data.get("aircraft_make_model")), value_style)
        ],
    ]
    
    aircraft_table = Table(aircraft_info, colWidths=[2.5*inch, 4.5*inch])
    aircraft_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f1f5f9')),
        ('TEXTCOLOR', (0, 0), (0, -1), secondary_color),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ('ROUNDEDCORNERS', (0, 0), (-1, -1), 5),
    ]))
    story.append(aircraft_table)
    story.append(Spacer(1, 15))
    
    # Process each log entry
    for i, entry in enumerate(log_entries, 1):
        # Entry header
        story.append(Paragraph(f"Entry #{i}", entry_style))
        
        # Entry details in two columns
        left_column = []
        right_column = []
        
        # Work Description - Full width
        work_desc = safe_str(entry.get("description_of_work_performed"))
        if work_desc and work_desc != "Not specified":
            work_table_data = [[Paragraph(work_desc, normal_style)]]
            work_table = Table(work_table_data, colWidths=[7*inch])
            work_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#fef3c7')),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('LEFTPADDING', (0, 0), (-1, -1), 15),
                ('RIGHTPADDING', (0, 0), (-1, -1), 15),
                ('TOPPADDING', (0, 0), (-1, -1), 12),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('ROUNDEDCORNERS', (0, 0), (-1, -1), 5),
            ]))
            story.append(work_table)
            story.append(Spacer(1, 10))
        
        # Reason for Maintenance - Full width
        reason_for_maintenance = safe_str(entry.get("reason_for_maintenance"))
        if reason_for_maintenance and reason_for_maintenance != "Not specified":
            reason_table_data = [[Paragraph(reason_for_maintenance, normal_style)]]
            reason_table = Table(reason_table_data, colWidths=[7*inch])
            reason_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#dbeafe')),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('LEFTPADDING', (0, 0), (-1, -1), 15),
                ('RIGHTPADDING', (0, 0), (-1, -1), 15),
                ('TOPPADDING', (0, 0), (-1, -1), 12),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('ROUNDEDCORNERS', (0, 0), (-1, -1), 5),
            ]))
            story.append(reason_table)
            story.append(Spacer(1, 10))
        
        # Technician Information
        tech_info = [
            [Paragraph("Performed By", label_style), Paragraph(safe_str(entry.get("performed_by")), value_style)],
            [Paragraph("License Number", label_style), Paragraph(safe_str(entry.get("license_number")), value_style)],
            [Paragraph("Date", label_style), Paragraph(safe_str(entry.get("date")), value_style)],
            [Paragraph("Tach Time", label_style), Paragraph(safe_str(entry.get("tach_time")), value_style)],
            [Paragraph("Hobbs Time", label_style), Paragraph(safe_str(entry.get("hobbs_time")), value_style)],
        ]
        tech_table = Table(tech_info, colWidths=[1.8*inch, 2.2*inch])
        tech_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f1f5f9')),
            ('TEXTCOLOR', (0, 0), (0, -1), secondary_color),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
            ('ROUNDEDCORNERS', (0, 0), (-1, -1), 3),
        ]))
        left_column.append(Paragraph("Technician Info", section_style))
        left_column.append(tech_table)
        left_column.append(Spacer(1, 10))
        
        # Risk Assessment
        risk_level = safe_str(entry.get("risk_level"))
        urgency = safe_str(entry.get("urgency"))
        is_airworthy = entry.get("is_airworthy", False)
        
        risk_info = [
            [Paragraph("Risk Level", label_style), Paragraph(risk_level, value_style)],
            [Paragraph("Urgency", label_style), Paragraph(urgency, value_style)],
            [Paragraph("Airworthy", label_style), Paragraph("Yes" if is_airworthy else "No", value_style)],
        ]
        risk_table = Table(risk_info, colWidths=[1.8*inch, 2.2*inch])
        risk_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f1f5f9')),
            ('TEXTCOLOR', (0, 0), (0, -1), secondary_color),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
            ('ROUNDEDCORNERS', (0, 0), (-1, -1), 3),
        ]))
        right_column.append(Paragraph("Risk Assessment", section_style))
        right_column.append(risk_table)
        right_column.append(Spacer(1, 10))
        
        # Compliance Information
        compliance_info = [
            [Paragraph("AD Compliance", label_style), Paragraph(safe_str(entry.get("ad_compliance")), value_style)],
            [Paragraph("Next Due", label_style), Paragraph(safe_str(entry.get("next_due_compliance")), value_style)],
            [Paragraph("Service Bulletin", label_style), Paragraph(safe_str(entry.get("service_bulletin_reference")), value_style)],
            [Paragraph("Manual Ref", label_style), Paragraph(safe_str(entry.get("manual_reference")), value_style)],
        ]
        compliance_table = Table(compliance_info, colWidths=[1.8*inch, 2.2*inch])
        compliance_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f1f5f9')),
            ('TEXTCOLOR', (0, 0), (0, -1), secondary_color),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
            ('ROUNDEDCORNERS', (0, 0), (-1, -1), 3),
        ]))
        left_column.append(Paragraph("Compliance", section_style))
        left_column.append(compliance_table)
        left_column.append(Spacer(1, 10))
        
        # Part Numbers
        part_numbers = entry.get("part_number_replaced", [])
        if part_numbers and isinstance(part_numbers, list) and len(part_numbers) > 0:
            parts_text = "<br/>".join([f"• {safe_str(part)}" for part in part_numbers])
            parts_para = Paragraph(parts_text, normal_style)
            parts_table_data = [[parts_para]]
            parts_table = Table(parts_table_data, colWidths=[4*inch])
            parts_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#fef3c7')),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('LEFTPADDING', (0, 0), (-1, -1), 8),
                ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('ROUNDEDCORNERS', (0, 0), (-1, -1), 3),
            ]))
            right_column.append(Paragraph("Parts Replaced", section_style))
            right_column.append(parts_table)
            right_column.append(Spacer(1, 10))
        
        # Combine left and right columns for this entry
        if left_column and right_column:
            combined_data = [[left_column, right_column]]
            combined_table = Table(combined_data, colWidths=[3.5*inch, 3.5*inch])
            combined_table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (0, -1), 0),
                ('RIGHTPADDING', (1, 0), (1, -1), 0),
            ]))
            story.append(combined_table)
        
        # Certification Statement - Full width at bottom of entry
        cert_statement = safe_str(entry.get("certification_statement"))
        if cert_statement and cert_statement != "Not specified":
            story.append(Spacer(1, 10))
            cert_table_data = [[Paragraph(cert_statement, normal_style)]]
            cert_table = Table(cert_table_data, colWidths=[7*inch])
            cert_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#ecfdf5')),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('LEFTPADDING', (0, 0), (-1, -1), 15),
                ('RIGHTPADDING', (0, 0), (-1, -1), 15),
                ('TOPPADDING', (0, 0), (-1, -1), 12),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('ROUNDEDCORNERS', (0, 0), (-1, -1), 5),
            ]))
            story.append(cert_table)
        
        # Add separator between entries (except for last entry)
        if i < len(log_entries):
            story.append(Spacer(1, 20))
            story.append(Paragraph("─" * 50, ParagraphStyle(
                'Separator',
                parent=styles['Normal'],
                fontSize=8,
                alignment=TA_CENTER,
                textColor=secondary_color
            )))
            story.append(Spacer(1, 20))
    
    # Footer
    story.append(Spacer(1, 20))
    footer_text = f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Aircraft Maintenance Log System"
    story.append(Paragraph(footer_text, ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        alignment=TA_CENTER,
        textColor=secondary_color
    )))
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer

@router.post("/logs/{log_id}/export")
async def export_log(log_id: str, export_request: ExportRequest):
    """
    Export a maintenance log to JSON or PDF
    """
    print(f"=== EXPORT LOG START === Log ID: {log_id}, Format: {export_request.format}")
    try:
        # Validate ObjectId
        if not ObjectId.is_valid(log_id):
            raise HTTPException(status_code=400, detail="Invalid log ID format")
        
        collection = Database.get_collection()
        doc = await collection.find_one({"_id": ObjectId(log_id)})
        
        if not doc:
            raise HTTPException(status_code=404, detail="Maintenance log not found")
        
        print(f"✅ Document found for export")
        
        if export_request.format.lower() == "json":
            # Return JSON response
            print(f"📄 Exporting as JSON")
            print(f"📝 Response data:")
            print(f"   - Format: JSON")
            print(f"   - Log ID: {log_id}")
            print(f"   - Content type: application/json")
            print(f"   - Filename: maintenance_log_{log_id}.json")
            return JSONResponse(
                content=doc,
                media_type="application/json",
                headers={"Content-Disposition": f"attachment; filename=maintenance_log_{log_id}.json"}
            )
        
        elif export_request.format.lower() == "pdf":
            # Generate PDF
            print(f"📄 Generating PDF report")
            pdf_buffer = generate_maintenance_log_pdf(doc)
            
            print(f"✅ PDF generated successfully")
            print(f"📝 Response data:")
            print(f"   - Format: PDF")
            print(f"   - Log ID: {log_id}")
            print(f"   - Content type: application/pdf")
            print(f"   - Filename: maintenance_log_{log_id}.pdf")
            print(f"   - PDF size: {len(pdf_buffer.getvalue())} bytes")
            return StreamingResponse(
                BytesIO(pdf_buffer.getvalue()),
                media_type="application/pdf",
                headers={"Content-Disposition": f"attachment; filename=maintenance_log_{log_id}.pdf"}
            )
        
        else:
            raise HTTPException(status_code=400, detail="Unsupported export format. Use 'json' or 'pdf'")
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ ERROR in export_log: {e}")
        import traceback
        print(f"❌ ERROR traceback: {traceback.format_exc()}")
        logger.error(f"Error exporting log {log_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to export log: {str(e)}")

@router.delete("/logs/{log_id}")
async def delete_log(log_id: str):
    """
    Delete a maintenance log
    """
    print(f"=== DELETE LOG START === Log ID: {log_id}")
    try:
        # Validate ObjectId
        print(f"🔄 Validating ObjectId: {log_id}")
        if not ObjectId.is_valid(log_id):
            print(f"❌ Invalid ObjectId format: {log_id}")
            raise HTTPException(status_code=400, detail="Invalid log ID format")
        
        print(f"✅ ObjectId validation passed")
        
        collection = Database.get_collection()
        print(f"✅ Database collection obtained")
        
        print(f"🔄 Attempting to delete document with _id: {ObjectId(log_id)}")
        result = await collection.delete_one({"_id": ObjectId(log_id)})
        
        print(f"📝 Delete result: {result}")
        print(f"📝 Deleted count: {result.deleted_count}")
        
        if result.deleted_count == 0:
            print(f"❌ No document found to delete")
            raise HTTPException(status_code=404, detail="Maintenance log not found")
        
        print(f"✅ Document deleted successfully")
        print(f"📝 Response data:")
        print(f"   - Deleted count: {result.deleted_count}")
        print(f"   - Message: Maintenance log deleted successfully")
        
        return {"message": "Maintenance log deleted successfully"}
        
    except HTTPException:
        print(f"❌ HTTPException raised, re-raising")
        raise
    except Exception as e:
        print(f"❌ ERROR in delete_log: {e}")
        import traceback
        print(f"❌ ERROR traceback: {traceback.format_exc()}")
        logger.error(f"Error deleting log {log_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete log: {str(e)}")

@router.get("/logs/search/{aircraft_registration}")
async def search_logs_by_aircraft(aircraft_registration: str):
    """
    Search maintenance logs by aircraft registration
    """
    print(f"=== SEARCH LOGS START === Aircraft: {aircraft_registration}")
    try:
        collection = Database.get_collection()
        cursor = collection.find({
            "structured_data.aircraft_registration": {"$regex": aircraft_registration, "$options": "i"}
        }).sort("timestamp", -1)
        
        logs = []
        async for doc in cursor:
            # Convert the _id to string for proper Pydantic validation
            doc["_id"] = str(doc["_id"])
            logs.append(MaintenanceLog(**doc))
        
        print(f"✅ Search completed successfully")
        print(f"📝 Response data:")
        print(f"   - Search term: {aircraft_registration}")
        print(f"   - Number of results: {len(logs)}")
        for i, log in enumerate(logs):
            print(f"   - Result {i+1}:")
            print(f"     * ID: {log.id}")
            print(f"     * Aircraft: {log.structured_data.aircraft_registration if log.structured_data else 'Unknown'}")
            print(f"     * Timestamp: {log.timestamp}")
        
        return logs
        
    except Exception as e:
        print(f"❌ ERROR in search_logs_by_aircraft: {e}")
        import traceback
        print(f"❌ ERROR traceback: {traceback.format_exc()}")
        logger.error(f"Error searching logs for aircraft {aircraft_registration}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to search logs: {str(e)}")

@router.get("/images/{image_filename:path}")
async def get_image(image_filename: str):
    """
    Serve uploaded maintenance log images
    """
    print(f"=== GET IMAGE START === Filename: {image_filename}")
    try:
        # Create uploads directory if it doesn't exist
        uploads_dir = Path("uploads")
        uploads_dir.mkdir(exist_ok=True)
        print(f"📝 Uploads directory path: {uploads_dir.absolute()}")
        
        # Decode the URL-encoded filename
        decoded_filename = unquote(image_filename)
        print(f"📝 Decoded filename: {decoded_filename}")
        
        image_path = uploads_dir / decoded_filename
        print(f"📝 Requested image path: {image_path.absolute()}")
        print(f"📝 Image exists: {image_path.exists()}")
        
        if not image_path.exists():
            print(f"❌ Image not found: {image_path.absolute()}")
            raise HTTPException(status_code=404, detail="Image not found")
        
        print(f"✅ Image found, serving: {image_path.absolute()}")
        print(f"📝 File size: {image_path.stat().st_size} bytes")
        print(f"📝 Response data:")
        print(f"   - Filename: {decoded_filename}")
        print(f"   - File path: {image_path.absolute()}")
        print(f"   - File size: {image_path.stat().st_size} bytes")
        print(f"   - Media type: image/*")
        
        return FileResponse(
            path=str(image_path),
            media_type="image/*",
            filename=decoded_filename
        )
        
    except HTTPException:
        print(f"❌ HTTPException raised, re-raising")
        raise
    except Exception as e:
        print(f"❌ ERROR in get_image: {e}")
        import traceback
        print(f"❌ ERROR traceback: {traceback.format_exc()}")
        logger.error(f"Error serving image {image_filename}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to serve image: {str(e)}") 