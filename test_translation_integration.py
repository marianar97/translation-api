import asyncio
import logging
import multiprocessing
from typing import Any, Dict
from uuid import UUID
from fastapi.testclient import TestClient
import pytest
import uvicorn
from time import sleep

from server import app as server_app
from client import app as client_app
from client.models import Status

client = TestClient(client_app)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)


def run_server():
    uvicorn.run(
        "server.server:app",  
        host="0.0.0.0",
        port=5000,
        reload=False
    )

def start_server():
    server_process = multiprocessing.Process(target=run_server)
    server_process.start()
    sleep(2)  # Give the server time to start
    return server_process

def stop_server(server_process):
    server_process.terminate()
    server_process.join()

@pytest.fixture(scope="module")
def server():
    process = start_server()
    yield process
    stop_server(process)


async def create_job(request_data: Dict[str, Any]) -> Dict[str, Any]:
    response = client.post("/translations/job/", json=request_data)
    assert response.status_code == 201
    return response.json()

async def create_job(request_data: Dict[str, Any]) -> Dict[str, Any]:
    try:
        response = client.post("/translations/job/", json=request_data)
        logger.debug(f"Create job response status: {response.status_code}")
        logger.debug(f"Create job response body: {response.json()}")
        
        assert response.status_code == 201
        return response.json()
    except Exception as e:
        logger.error(f"Error creating job: {str(e)}")
        raise
    
async def check_job_status(job_id: str) -> Dict[str, Any]:
    try:
        response = client.get(f"/translations/job/{job_id}")
        logger.debug(f"Check status response status: {response.status_code}")
        logger.debug(f"Check status response body: {response.json()}")
        
        assert response.status_code == 200
        return response.json()
    except Exception as e:
        logger.error(f"Error checking job status: {str(e)}")
        raise
   
@pytest.mark.asyncio
async def test_successful_translation_job(server):
    """Test a successful translation job with valid parameters"""
    request_data = {
        "duration": 1,
        "webhook_url": "https://webhook.site/94070b61-3ca5-4a17-8fc0-db7b8a8c1c8c"
    }
    
    # Create job and log response
    job_data = await create_job(request_data)
    logger.info(f"Created job with data: {job_data}")
    job_id = job_data["id"]
    
    # Initial validation
    assert job_data["duration"] == request_data["duration"]
    assert job_data["webhook_url"] == request_data["webhook_url"]
    assert "status" in job_data, f"Status key missing in response: {job_data}"
    assert job_data["status"] in [Status.PENDING, Status.ERROR]
    assert UUID(job_id)
    
    # Wait and check status
    if job_data["status"] == Status.PENDING:
        duration = job_data["duration"]
        logger.info(f"Waiting for {duration} seconds...")
        sleep(duration + 1)
        
        # Get final status
        final_status = await check_job_status(job_id)
        logger.info(f"Final job status: {final_status}")
        
        # Verify the response contains required fields
        assert "status" in final_status, f"Status missing in final response: {final_status}"
        assert final_status["status"] == Status.COMPLETED, f"Unexpected status: {final_status['status']}"

@pytest.mark.asyncio
async def test_invalid_duration(server):
    """Test job creation with invalid duration"""
    request_data = {
        "duration": -1,
        "webhook_url": "https://webhook.site/test"
    }
    
    response = client.post("/translations/job/", json=request_data)
    assert response.status_code == 422  # Validation error

@pytest.mark.asyncio
async def test_invalid_webhook_url(server):
    """Test job creation with invalid webhook URL"""
    request_data = {
        "duration": 1,
        "webhook_url": "invalid-url"
    }
    
    response = client.post("/translations/job/", json=request_data)
    assert response.status_code == 422  # Validation error
    
@pytest.mark.asyncio
async def test_nonexistent_job(server):
    """Test retrieving a non-existent job"""
    fake_id = str(UUID(int=0))
    response = client.get(f"/translation/job/{fake_id}")
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_concurrent_jobs(server):
    """Test creating multiple jobs concurrently"""
    request_data = {
        "duration": 1,
        "webhook_url": "https://webhook.site/94070b61-3ca5-4a17-8fc0-db7b8a8c1c8c"
    }
    
    # Create multiple jobs
    responses = []
    for _ in range(3):
        response = client.post("/translations/job/", json=request_data)
        assert response.status_code == 201
        responses.append(response.json())
    
    # Verify each job has unique ID
    job_ids = [r["id"] for r in responses]
    assert len(set(job_ids)) == len(job_ids)
    
    # Wait for completion
    sleep(2)
    
    # Check all jobs completed or error
    for job_id in job_ids:
        response = client.get(f"/translations/job/{job_id}")
        assert response.status_code == 200
        final_status = response.json()
        assert final_status["status"] in [Status.COMPLETED, Status.ERROR]