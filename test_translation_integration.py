import asyncio
import logging
import multiprocessing
from uuid import UUID
from fastapi.testclient import TestClient
import pytest
import uvicorn
from time import sleep
from httpx import AsyncClient

from server import app as server_app
from client import app as client_app
from client.models import Status

# client = TestClient(client_app)

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

import asyncio
import logging
import multiprocessing
from uuid import UUID
import pytest
import uvicorn
from time import sleep
from httpx import AsyncClient

from server import app as server_app
from client import app as client_app
from client.models import Status

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

@pytest.mark.asyncio
async def test_integration_test(server):
    # Specify the base URL for the client
    base_url = "http://localhost:5000"
    
    async with AsyncClient(app=client_app, base_url=base_url) as client:
        request_data = {
            "duration": 1,
            "webhook_url": "http://example.com/webhook"
        }

        # Create the job
        response = await client.post("/translations/job", json=request_data)
        assert response.status_code == 201

        # job_data = response.json()
        # job_id = job_data["id"]

        # # Initial validation
        # assert job_data["duration"] == request_data["duration"]
        # assert job_data["webhook_url"] == request_data["webhook_url"]
        # assert job_data["status"] in [Status.PENDING, Status.ERROR]
        # assert UUID(job_id)

        # async def check_job_status(job_id: str, timeout: int = 10) -> bool:
        #     start_time = asyncio.get_event_loop().time()
        #     while asyncio.get_event_loop().time() - start_time < timeout:
        #         response = await client.get(f"/translation/job/{job_id}")
        #         if response.status_code == 200:
        #             job = response.json()
        #             if job["status"] in [Status.COMPLETED, Status.ERROR]:
        #                 return True
        #         await asyncio.sleep(0.5)
        #     return False

        # # Wait for job completion
        # job_completed = await check_job_status(job_id)

        # # Final status check
        # final_response = await client.get(f"/translation/job/{job_id}")
        # assert final_response.status_code == 200
        # final_job = final_response.json()

        # # Verify final state
        # assert final_job["id"] == job_id
        # assert final_job["status"] in [Status.COMPLETED, Status.ERROR, Status.PENDING]