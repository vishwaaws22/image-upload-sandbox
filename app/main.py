"""HTTP API. Day 2 starter: health check and upload-request validation.

Later days add: presigned S3 upload URLs (Day 5) and image metadata in a database (Day 6).
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from app import __version__
from app.config import get_settings
from app.validation import UploadRejected, object_key, validate_upload

app = FastAPI(title="Image Upload API", version=__version__)


class UploadRequest(BaseModel):
    owner_id: str = Field(examples=["customer-001"])
    filename: str = Field(examples=["invoice-photo.jpg"])
    content_type: str = Field(examples=["image/jpeg"])
    size_bytes: int = Field(examples=[204800])


class UploadPlan(BaseModel):
    object_key: str
    content_type: str
    max_bytes: int
    upload_url: str | None = None  # filled in on Day 5 (presigned S3 URL)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "version": __version__, "env": get_settings().app_env}


@app.post("/uploads", response_model=UploadPlan, status_code=201)
def request_upload(body: UploadRequest) -> UploadPlan:
    """Check an upload request and return where the image will be stored."""
    settings = get_settings()
    try:
        validate_upload(body.filename, body.content_type, body.size_bytes, settings)
        key = object_key(body.owner_id, body.filename)
    except UploadRejected as err:
        raise HTTPException(status_code=422, detail=str(err)) from err
    return UploadPlan(
        object_key=key, content_type=body.content_type, max_bytes=settings.max_upload_bytes
    )
