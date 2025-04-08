from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse, JSONResponse
import subprocess
import os
import uuid
import shutil
import logging
from typing import Optional

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

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
    logger.debug(f"File extension: {ext}")
    
    if ext not in ALLOWED_FORMATS[format]:
        raise HTTPException(
            status_code=400, 
            detail=f"Converting from {ext} to {format} not supported. Supported source formats for {format}: {', '.join(ALLOWED_FORMATS[format])}"
        )
    
    # Create temp directory
    work_dir = os.path.join(TEMP_DIR, f"convert_{uuid.uuid4().hex}")
    os.makedirs(work_dir, exist_ok=True)
    logger.debug(f"Created temp directory: {work_dir}")
    
    try:
        # Save uploaded file
        input_path = os.path.join(work_dir, f"input.{ext}")
        logger.debug(f"Saving file to: {input_path}")
        
        content = await file.read()
        logger.debug(f"Read {len(content)} bytes from uploaded file")
        
        with open(input_path, "wb") as f:
            f.write(content)
        
        logger.debug(f"File saved, checking if it exists: {os.path.exists(input_path)}")
        
        # Run conversion
        logger.debug("Starting LibreOffice conversion")
        cmd = [
            "libreoffice",
            "--headless",
            "--convert-to", format,
            "--outdir", work_dir,
            input_path
        ]
        logger.debug(f"Running command: {' '.join(cmd)}")
        
        process = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True
        )
        
        logger.debug(f"LibreOffice return code: {process.returncode}")
        logger.debug(f"LibreOffice stdout: {process.stdout}")
        logger.debug(f"LibreOffice stderr: {process.stderr}")
        
        if process.returncode != 0:
            logger.error(f"Conversion failed: {process.stderr}")
            return JSONResponse(
                status_code=500, 
                content={"error": f"Conversion failed: {process.stderr}"}
            )
        
        # Find output file (LibreOffice keeps the original filename but changes the extension)
        expected_output = os.path.join(work_dir, f"input.{format}")
        logger.debug(f"Looking for output file: {expected_output}")
        logger.debug(f"Directory contents: {os.listdir(work_dir)}")
        
        if not os.path.exists(expected_output):
            logger.error(f"Output file not found: {expected_output}")
            return JSONResponse(
                status_code=500,
                content={"error": "Output file not found after conversion"}
            )
        
        # Copy the file to a more permanent location
        output_dir = os.path.join(TEMP_DIR, "outputs")
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, f"{uuid.uuid4().hex}.{format}")
        shutil.copy2(expected_output, output_file)
        logger.debug(f"Copied converted file to: {output_file}")
        
        # Return file
        logger.debug(f"Returning converted file: {output_file}")
        
        # Set background cleanup for the temporary output file
        @app.on_event("startup")
        async def cleanup_old_files():
            try:
                if os.path.exists(output_dir):
                    for old_file in os.listdir(output_dir):
                        try:
                            os.remove(os.path.join(output_dir, old_file))
                        except Exception:
                            pass
            except Exception:
                pass
        
        return FileResponse(
            output_file,
            media_type=f"application/{format}",
            filename=f"converted.{format}"
        )
    except Exception as e:
        logger.exception(f"Error during conversion: {str(e)}")
        if not isinstance(e, HTTPException):
            return JSONResponse(
                status_code=500,
                content={"error": f"Conversion failed: {str(e)}"}
            )
        raise
    finally:
        # Clean up temporary directory
        try:
            if os.path.exists(work_dir):
                logger.debug(f"Cleaning up temp directory: {work_dir}")
                shutil.rmtree(work_dir, ignore_errors=True)
        except Exception as e:
            logger.warning(f"Failed to clean up temporary files: {str(e)}")

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