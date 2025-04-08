from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
import subprocess
import os
import uuid
import shutil
from typing import Optional

app = FastAPI(title="Document Converter")

ALLOWED_FORMATS = {
    "docx": ["doc"],
    "pdf": ["doc", "docx"]
}
TEMP_DIR = "/tmp"

@app.post("/convert")
async def convert_document(
    file: UploadFile = File(...),
    format: str = "docx"
):
    """
    Convert a document from one format to another.
    
    - **file**: The document file to convert
    - **format**: Target format (default: docx)
    
    Supported conversions:
    - doc → docx
    - doc → pdf
    - docx → pdf
    """
    # Validate format
    if format not in ALLOWED_FORMATS:
        raise HTTPException(
            status_code=400, 
            detail=f"Format {format} not supported. Supported formats: {', '.join(ALLOWED_FORMATS.keys())}"
        )
    
    # Validate file exists and has filename
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")
    
    # Get file extension
    ext = os.path.splitext(file.filename)[1][1:].lower()
    if ext not in ALLOWED_FORMATS[format]:
        raise HTTPException(
            status_code=400, 
            detail=f"Converting from {ext} to {format} not supported. Supported source formats for {format}: {', '.join(ALLOWED_FORMATS[format])}"
        )
    
    # Create temp directory
    work_dir = os.path.join(TEMP_DIR, f"convert_{uuid.uuid4().hex}")
    os.makedirs(work_dir, exist_ok=True)
    
    try:
        # Save uploaded file
        input_path = os.path.join(work_dir, f"input.{ext}")
        with open(input_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Run conversion
        process = subprocess.run([
            "libreoffice",
            "--headless",
            "--convert-to", format,
            "--outdir", work_dir,
            input_path
        ], capture_output=True, text=True)
        
        if process.returncode != 0:
            raise HTTPException(
                status_code=500, 
                detail=f"Conversion failed: {process.stderr}"
            )
        
        # Find output file (LibreOffice keeps the original filename but changes the extension)
        output_file = os.path.join(work_dir, f"input.{format}")
        if not os.path.exists(output_file):
            raise HTTPException(status_code=500, detail="Output file not found")
        
        # Return file
        return FileResponse(
            output_file,
            media_type=f"application/{format}",
            filename=f"converted.{format}"
        )
    except Exception as e:
        if not isinstance(e, HTTPException):
            raise HTTPException(status_code=500, detail=str(e))
        raise
    finally:
        # Clean up temporary directory
        try:
            shutil.rmtree(work_dir, ignore_errors=True)
        except Exception:
            pass

@app.get("/")
def read_root():
    """Return service information and supported conversions."""
    return {
        "service": "Document Converter",
        "supported_conversions": [
            {"from": source, "to": target}
            for target, sources in ALLOWED_FORMATS.items()
            for source in sources
        ],
        "usage": "POST /convert with file upload and format parameter"
    } 