# image-upload-api

Customer image-upload API: the capstone application of the AWS Cloud & Application Deployment Training.
The same repository is used from Day 2 to Day 7.

| Day | What is added |
|---|---|
| 2 | This starter: health check, upload-request validation, tests, lint, CI workflow |
| 4 | Dockerfile and Compose file; runs as a container on EC2 with an EBS-backed directory |
| 5 | Presigned S3 upload URL in the `POST /uploads` response; deployed on Render |
| 6 | Image metadata in a database; list a customer's own images |
| 7 | Monitoring, runbook, final demo |

## Requirements

Python 3.11 or newer (FastAPI 0.165 needs at least 3.11). On Amazon Linux 2023:

```bash
sudo dnf install -y python3.11 python3.11-pip git
```

## Run it on Windows (PowerShell)

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

If activation is blocked, run `Set-ExecutionPolicy -Scope Process RemoteSigned` in that window first.
In a second PowerShell window:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
$body = '{"owner_id":"customer-001","filename":"photo.jpg","content_type":"image/jpeg","size_bytes":204800}'
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/uploads -ContentType 'application/json' -Body $body
```

## Run it on Linux (EC2 host, from Day 4)

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

In a second terminal:

```bash
curl -s http://127.0.0.1:8000/health
curl -s -X POST http://127.0.0.1:8000/uploads -H 'Content-Type: application/json' \
  -d '{"owner_id":"customer-001","filename":"photo.jpg","content_type":"image/jpeg","size_bytes":204800}'
```

Interactive API documentation: `http://127.0.0.1:8000/docs`.

## Endpoints

| Method and path | Purpose | Success | Failure |
|---|---|---|---|
| `GET /health` | Liveness check (used by Render and by monitoring) | 200 `{"status":"ok",...}` | - |
| `POST /uploads` | Validate an upload request and return the storage key | 201 with `object_key` | 422 with the broken rule |

Validation rules (`app/validation.py`): content type is `image/jpeg` or `image/png`; the file extension
matches the content type; the file name has only letters, digits, `.`, `_`, `-`; the size is above 0 and
at most `MAX_UPLOAD_BYTES`; the storage key is `uploads/<owner_id>/<random>.<ext>`.

## Checks (the same three that CI runs)

```bash
ruff check .
ruff format --check .
pytest -q
```

`.github/workflows/ci.yml` runs them on every pull request and on every push to `main`.

## Configuration

Environment variables only; see `.env.example`. Never commit `.env`, keys or tokens.

| Variable | Default | Meaning |
|---|---|---|
| `APP_ENV` | `local` | Shown by `/health` |
| `MAX_UPLOAD_BYTES` | `5242880` | Largest accepted image (5 MiB) |
| `ALLOWED_CONTENT_TYPES` | `image/jpeg,image/png` | Accepted content types |

## Layout

```text
app/main.py         routes
app/validation.py   upload rules and storage-key naming
app/config.py       settings from environment variables
tests/              pytest tests
render.yaml         Render blueprint (used on Day 5)
```
