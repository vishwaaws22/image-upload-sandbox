import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

GOOD = {
    "owner_id": "customer-001",
    "filename": "photo.jpg",
    "content_type": "image/jpeg",
    "size_bytes": 204800,
}


def test_valid_request_returns_customer_scoped_key():
    response = client.post("/uploads", json=GOOD)
    assert response.status_code == 201
    body = response.json()
    assert body["object_key"].startswith("uploads/customer-001/")
    assert body["object_key"].endswith(".jpg")
    assert body["upload_url"] is None


def test_two_uploads_of_the_same_name_get_different_keys():
    first = client.post("/uploads", json=GOOD).json()["object_key"]
    second = client.post("/uploads", json=GOOD).json()["object_key"]
    assert first != second


@pytest.mark.parametrize(
    "change",
    [
        {"content_type": "application/pdf", "filename": "doc.pdf"},
        {"filename": "photo.png"},  # extension does not match image/jpeg
        {"filename": "../../etc/passwd.jpg"},
        {"size_bytes": 0},
        {"size_bytes": 50 * 1024 * 1024},
        {"owner_id": "../other-customer"},
    ],
)
def test_bad_requests_are_rejected(change):
    response = client.post("/uploads", json={**GOOD, **change})
    assert response.status_code == 422
