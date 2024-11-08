import asyncio
import logging
import multiprocessing
from uuid import UUID
from fastapi.testclient import TestClient
import pytest
import uvicorn
from time import sleep

from server import app as server_app
from client import app as client_app
from client.models import Status


# Initialize server and client instances for testing
# client = TestClient(server_app)
client_client = TestClient(client_app)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def run_server():
    uvicorn.run(
        "server.server:app",  
        host="0.0.0.0",
        port=8000,
        reload=False
    )

def start_server():
    server_process = multiprocessing.Process(target=run_server)
    server_process.start()
    # Give the server time to start
    sleep(2)
    return server_process


def stop_server(server_process):
    server_process.terminate()
    server_process.join()

def test_integration_test():
    # Start the server
    start_server()
    
    # Test creating a new translation job
    request_data = {
        "duration": 1,
        "webhook_url": "http://example.com/webhook"
    }
    response = client_client.post("/translations/job/", json=request_data)
    # sleep(40000)
    
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["duration"] == request_data["duration"]
    assert data["webhook_url"] == request_data["webhook_url"]
    assert "status" in data
    assert data["status"] in [Status.PENDING, Status.ERROR]
    assert UUID(data["id"])

