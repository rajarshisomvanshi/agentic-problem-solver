import shutil
import uuid
from pathlib import Path
from typing import List

from fastapi import APIRouter, UploadFile, File, HTTPException, Request
from pydantic import BaseModel

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

router = APIRouter()

UPLOAD_DIR = Path("data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

class UploadResponse(BaseModel):
    file_id: str
    filename: str
    path: str
    content_type: str

@router.post("/upload", response_model=UploadResponse)
async def upload_file(request: Request, file: UploadFile = File(...)):
    try:
        # Check Content-Length header first
        content_length = request.headers.get('content-length')
        if content_length and int(content_length) > MAX_FILE_SIZE:
             raise HTTPException(status_code=413, detail="File too large. Maximum size is 10MB.")

        file_id = str(uuid.uuid4())
        extension = Path(file.filename).suffix
        new_filename = f"{file_id}{extension}"
        file_path = UPLOAD_DIR / new_filename

        # Copy and check size
        size = 0
        with file_path.open("wb") as buffer:
            while chunk := await file.read(1024 * 1024): # Read in 1MB chunks
                size += len(chunk)
                if size > MAX_FILE_SIZE:
                    file_path.unlink(missing_ok=True) # Delete partial file
                    raise HTTPException(status_code=413, detail="File too large. Maximum size is 10MB.")
                buffer.write(chunk)
        
        return {
            "file_id": file_id,
            "filename": file.filename,
            "path": str(file_path),
            "content_type": file.content_type
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
