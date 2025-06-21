import os
import uuid
from pathlib import Path
from typing import List, Optional
from fastapi import HTTPException, UploadFile

# Constants
UPLOAD_DIR = "uploads/waste-reports"
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
MAX_FILES_PER_REPORT = 10
ALLOWED_MIME_TYPES = {"image/jpeg", "image/png"}


class FileUploadService:
    def __init__(self):
        self.upload_dir = Path(UPLOAD_DIR)
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    def validate_file(self, file: UploadFile) -> None:
        """Validate uploaded file for security and constraints"""
        
        # Check file size
        if hasattr(file, 'size') and file.size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"File size exceeds maximum allowed size of {MAX_FILE_SIZE // (1024*1024)}MB"
            )
        
        # Check file extension
        if file.filename:
            ext = Path(file.filename).suffix.lower()
            if ext not in ALLOWED_EXTENSIONS:
                raise HTTPException(
                    status_code=400,
                    detail=f"File type '{ext}' not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
                )
        
        # Check MIME type
        if file.content_type not in ALLOWED_MIME_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"MIME type '{file.content_type}' not allowed"
            )

    def validate_file_content(self, file_path: Path) -> None:
        """Additional validation of file content using basic file checks"""
        try:
            # Basic file existence and readability check
            if not file_path.exists():
                raise HTTPException(
                    status_code=400,
                    detail="File was not saved properly"
                )
            
            # Check if file is not empty
            if file_path.stat().st_size == 0:
                raise HTTPException(
                    status_code=400,
                    detail="File is empty"
                )
            
            # Basic image file validation by checking file headers
            with open(file_path, 'rb') as f:
                header = f.read(10)
                
                # Check for common image file signatures
                is_valid_image = False
                
                # JPEG signature
                if header.startswith(b'\xff\xd8\xff'):
                    is_valid_image = True
                # PNG signature
                elif header.startswith(b'\x89PNG\r\n\x1a\n'):
                    is_valid_image = True
                
                if not is_valid_image:
                    raise HTTPException(
                        status_code=400,
                        detail="Invalid image file format"
                    )
                
        except HTTPException:
            # Clean up the file if validation fails
            if file_path.exists():
                file_path.unlink()
            raise
        except Exception as e:
            # Clean up the file if validation fails
            if file_path.exists():
                file_path.unlink()
            raise HTTPException(
                status_code=400,
                detail="Invalid image file"
            )

    def generate_unique_filename(self, original_filename: str) -> str:
        """Generate unique filename while preserving extension"""
        if not original_filename:
            original_filename = "unnamed.jpg"
        
        ext = Path(original_filename).suffix.lower()
        unique_id = str(uuid.uuid4())
        return f"{unique_id}{ext}"

    def create_report_directory(self, report_id: int) -> Path:
        """Create directory for specific waste report"""
        report_dir = self.upload_dir / str(report_id)
        report_dir.mkdir(parents=True, exist_ok=True)
        return report_dir

    async def save_file(self, file: UploadFile, report_id: int) -> str:
        """Save uploaded file and return the file path"""
        
        # Validate file before processing
        self.validate_file(file)
        
        # Create report directory
        report_dir = self.create_report_directory(report_id)
        
        # Generate unique filename
        filename = self.generate_unique_filename(file.filename)
        file_path = report_dir / filename
        
        try:
            # Save file
            with open(file_path, "wb") as buffer:
                content = await file.read()
                
                # Additional size check for actual content
                if len(content) > MAX_FILE_SIZE:
                    raise HTTPException(
                        status_code=413,
                        detail=f"File size exceeds maximum allowed size of {MAX_FILE_SIZE // (1024*1024)}MB"
                    )
                
                buffer.write(content)
            
            # Validate file content
            self.validate_file_content(file_path)
            
            # Return relative path for database storage
            return f"{UPLOAD_DIR}/{report_id}/{filename}"
            
        except HTTPException:
            # Clean up file if validation fails
            if file_path.exists():
                file_path.unlink()
            raise
        except Exception as e:
            # Clean up file if any error occurs
            if file_path.exists():
                file_path.unlink()
            raise HTTPException(
                status_code=500,
                detail="Failed to save file"
            )

    async def save_multiple_files(self, files: List[UploadFile], report_id: int) -> List[str]:
        """Save multiple files and return list of file paths"""
        
        if len(files) > MAX_FILES_PER_REPORT:
            raise HTTPException(
                status_code=400,
                detail=f"Maximum {MAX_FILES_PER_REPORT} files allowed per report"
            )
        
        file_paths = []
        saved_files = []
        
        try:
            for file in files:
                if file.filename:  # Skip empty files
                    file_path = await self.save_file(file, report_id)
                    file_paths.append(file_path)
                    saved_files.append(Path(file_path))
            
            return file_paths
            
        except Exception as e:
            # Clean up any files that were saved if an error occurs
            for file_path in saved_files:
                if file_path.exists():
                    file_path.unlink()
            raise

    def delete_file(self, file_path: str) -> None:
        """Delete a file from storage"""
        try:
            full_path = Path(file_path)
            if full_path.exists():
                full_path.unlink()
        except Exception:
            # Log error but don't raise exception for cleanup operations
            pass

    def delete_report_files(self, report_id: int) -> None:
        """Delete all files for a specific report"""
        try:
            report_dir = self.upload_dir / str(report_id)
            if report_dir.exists():
                for file_path in report_dir.iterdir():
                    if file_path.is_file():
                        file_path.unlink()
                report_dir.rmdir()
        except Exception:
            # Log error but don't raise exception for cleanup operations
            pass


# Global instance
file_upload_service = FileUploadService()
