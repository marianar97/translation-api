import asyncio
import logging
from uuid import UUID
from fastapi.testclient import TestClient
from server import app as server_app
from client import app as client_app
from client.models import Status


# Initialize server and client instances for testing
client = TestClient(server_app)
# client_client = TestClient(client_app)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def test_create_translation():
    # Test creating a new translation job
    request_data = {
        "duration": 20,
        "webhook_url": "http://example.com/webhook"
    }
    response = client.post("/translations/status/", json=request_data)
    
    
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["duration"] == request_data["duration"]
    assert data["webhook_url"] == request_data["webhook_url"]
    assert "status" in data
    assert data["status"] in [Status.PENDING, Status.ERROR]
    assert UUID(data["id"])

