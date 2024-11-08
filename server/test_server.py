from fastapi.testclient import TestClient
from server import app  # Import both app and client from your main app file
import pytest
from uuid import UUID
from server.models import TranslationRequest, JobResponse

# If you prefer to create a new test client instead of importing it:
# client = TestClient(app)
client = TestClient(app)

def test_create_translation():
    # Test creating a new translation job
    request_data = {
        "duration": 10,
        "webhook_url": "http://example.com/webhook"
    }
    response = client.post("/translations/status/", json=request_data)
    
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["duration"] == request_data["duration"]
    assert data["webhook_url"] == request_data["webhook_url"]
    assert "status" in data
    assert UUID(data["id"])  # Verify ID is valid UUID

def test_get_status_existing_job():
    # First create a job
    request_data = {
        "duration": 5,
        "webhook_url": "http://example.com/webhook"
    }
    create_response = client.post("/translations/status/", json=request_data)
    job_id = create_response.json()["id"]
    
    
    # Then get its status
    response = client.get(f"/translations/status/{job_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == job_id
    assert data["duration"] == request_data["duration"]
    assert data["webhook_url"] == request_data["webhook_url"]


# def test_get_status_nonexistent_job():
#     # Test getting status of non-existent job
#     fake_uuid = "123e4567-e89b-12d3-a456-426614174000"
#     response = client.get(f"/translations/status/{fake_uuid}")
#     assert response.status_code == 404
#     assert response.json()["detail"] == f"Job with id: {fake_uuid} was not found"

# def test_get_all_jobs():
#     # Clear jobs store first (if you have access to it)
#     from server import jobs_store  # Import jobs_store if you need to manipulate it
#     jobs_store.clear()
    
#     # Create a few jobs
#     jobs = [
#         {"duration": 5, "webhook_url": "http://example.com/webhook1"},
#         {"duration": 10, "webhook_url": "http://example.com/webhook2"},
#     ]
    
#     created_jobs = []
#     for job in jobs:
#         response = client.post("/translations/status/", json=job)
#         created_jobs.append(response.json())
    
#     # Get all jobs
#     response = client.get("/translations/status")
#     assert response.status_code == 200
#     data = response.json()
    
#     assert "jobs" in data
#     assert len(data["jobs"]) == len(jobs)
    
#     # Verify each job exists in the response
#     response_job_ids = {job["id"] for job in data["jobs"]}
#     created_job_ids = {job["id"] for job in created_jobs}
#     assert response_job_ids == created_job_ids

# def test_invalid_request_data():
#     # Test with missing required fields
#     response = client.post("/translations/status/", json={})
#     assert response.status_code == 422

#     # Test with invalid duration type
#     response = client.post("/translations/status/", 
#                           json={"duration": "invalid", 
#                                "webhook_url": "http://example.com/webhook"})
#     assert response.status_code == 422

#     # Test with invalid webhook URL
#     response = client.post("/translations/status/", 
#                           json={"duration": 5, 
#                                "webhook_url": "invalid-url"})
#     assert response.status_code == 422