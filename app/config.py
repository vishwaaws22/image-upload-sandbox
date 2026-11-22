"""Settings read from environment variables (never hard-code secrets)."""

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    app_env: str
    max_upload_bytes: int
    allowed_content_types: tuple[str, ...]


def get_settings() -> Settings:
    types = os.environ.get("ALLOWED_CONTENT_TYPES", "image/jpeg,image/png")
    return Settings(
        app_env=os.environ.get("APP_ENV", "local"),
        max_upload_bytes=int(os.environ.get("MAX_UPLOAD_BYTES", str(5 * 1024 * 1024))),
        allowed_content_types=tuple(t.strip() for t in types.split(",") if t.strip()),
    )
