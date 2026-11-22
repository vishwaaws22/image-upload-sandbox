"""Server-side checks for an upload request. The browser is never trusted."""

import re
import uuid

from app.config import Settings

_EXTENSIONS = {"image/jpeg": (".jpg", ".jpeg"), "image/png": (".png",)}
_SAFE_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,99}$")
_SAFE_OWNER = re.compile(r"^[a-z0-9][a-z0-9-]{0,39}$")


class UploadRejected(ValueError):
    """The upload request breaks a rule; the message is safe to show to the caller."""


def validate_upload(filename: str, content_type: str, size_bytes: int, settings: Settings) -> None:
    if content_type not in settings.allowed_content_types:
        raise UploadRejected(f"content type {content_type!r} is not allowed")
    if not _SAFE_NAME.match(filename):
        raise UploadRejected("file name has characters that are not allowed")
    if not filename.lower().endswith(_EXTENSIONS.get(content_type, ())):
        raise UploadRejected("file extension does not match the content type")
    if size_bytes <= 0:
        raise UploadRejected("file is empty")
    if size_bytes > settings.max_upload_bytes:
        raise UploadRejected(f"file is larger than {settings.max_upload_bytes} bytes")


def object_key(owner_id: str, filename: str) -> str:
    """Storage key: one prefix per customer, a random id so names never collide."""
    if not _SAFE_OWNER.match(owner_id):
        raise UploadRejected("owner id is not valid")
    extension = filename[filename.rfind(".") :].lower()
    return f"uploads/{owner_id}/{uuid.uuid4().hex}{extension}"
