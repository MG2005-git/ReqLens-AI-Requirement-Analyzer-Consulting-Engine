from fastapi import UploadFile, HTTPException
import os

ALLOWED_EXTENSTIONS = {".txt",".pdf"}
MAX_FILE_SIZE = 5 * 1024 * 1024 # 5 MB


def validate_file(file: UploadFile):
    ext = os.path.splitext(file.filename)[1].lower()

    if ext not in ALLOWED_EXTENSTIONS:
        raise HTTPException(
            status_code= 400,
            detail="Only PDF and TXT files are allowed"
        )
    
async def extract_text(file: UploadFile) -> str:
    ext = os.path.splitext(file.filename)[1].lower()

    if ext == ".txt":
        content = await file.read()
        return content.decode("utf-8")
    
    if ext == ".pdf":
        # placeholder
        return "update in phase 4"
    
    return ""