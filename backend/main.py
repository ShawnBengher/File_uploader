import os
import uuid
from datetime import datetime, timezone
from typing import List

from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import boto3
from botocore.exceptions import BotoCoreError, ClientError


load_dotenv()

AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "")
PORT = int(os.getenv("PORT", "8000"))
ALLOWED_ORIGINS = [o.strip() for o in os.getenv("ALLOWED_ORIGINS", "").split(",") if o.strip()]
MAX_FILE_MB = int(os.getenv("MAX_FILE_MB", "5"))
ALLOWED_MIME_TYPES = [t.strip() for t in os.getenv("ALLOWED_MIME_TYPES", "image/png,image/jpeg,text/plain,application/pdf").split(",") if t.strip()]

if not S3_BUCKET_NAME:
    raise RuntimeError("S3_BUCKET_NAME must be set in environment variables")

app = FastAPI(title="Challenge 1 File Uploader", version="1.0.0")

if ALLOWED_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def get_s3_client():
    return boto3.client("s3", region_name=AWS_REGION)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/upload")
async def upload_file(request: Request, file: UploadFile = File(...)):
    if file is None:
        raise HTTPException(status_code=400, detail="No file uploaded")

    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {file.content_type}")

    # Read into memory for size validation (sufficient for small MAX_FILE_MB)
    file_bytes = await file.read()
    file_size_bytes = len(file_bytes)
    max_bytes = MAX_FILE_MB * 1024 * 1024
    if file_size_bytes > max_bytes:
        raise HTTPException(status_code=400, detail=f"File exceeds {MAX_FILE_MB} MB limit")

    original_filename = file.filename or "upload.bin"
    extension = os.path.splitext(original_filename)[1]
    unique_id = uuid.uuid4().hex
    date_prefix = datetime.now(timezone.utc).strftime("%Y/%m/%d")
    object_key = f"uploads/{date_prefix}/{unique_id}{extension}"

    s3 = get_s3_client()

    metadata = {
        "original-filename": original_filename,
        "content-type": file.content_type or "application/octet-stream",
        "size-bytes": str(file_size_bytes),
        "uploaded-at": datetime.now(timezone.utc).isoformat(),
        "uploader-ip": request.client.host if request.client else "unknown",
    }

    try:
        s3.put_object(
            Bucket=S3_BUCKET_NAME,
            Key=object_key,
            Body=file_bytes,
            ContentType=file.content_type,
            Metadata=metadata,
        )
        presigned_url = s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": S3_BUCKET_NAME, "Key": object_key},
            ExpiresIn=3600,
        )
    except (BotoCoreError, ClientError) as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

    return JSONResponse(
        {
            "message": "Upload successful",
            "file": {
                "key": object_key,
                "filename": original_filename,
                "contentType": file.content_type,
                "sizeBytes": file_size_bytes,
            },
            "url": presigned_url,
        }
    )


def create_app():
    return app


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=PORT, reload=True)


