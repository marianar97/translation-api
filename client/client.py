from client.logger_config import logger
from fastapi import FastAPI, BackgroundTasks
from client.models import TranslationRequest, JobResponse
from client.services.translation_service import TranslationService

app = FastAPI(
    title="Translation API",
    description="API for handling translation jobs",
    version="1.0.0",
)


@app.post("/translations/job", status_code=201)
async def create_translation_job(
    request: TranslationRequest, background_tasks: BackgroundTasks
) -> JobResponse:
    job = await TranslationService.create_translation(request)
    logger.info(f"Created translation job with ID: {job.id}")
    background_tasks.add_task(TranslationService.monitor_job_status, job)
    logger.info(f"Background task added to monitor job status for job ID: {job.id}")
    return job


@app.get("/translations/job/{id}", status_code=200)
async def get_job(id: str):
    logger.info(f"Received request to get job with ID: {id}")
    job = await TranslationService.get_job(id)
    if job:
        logger.info(f"Job found with ID: {id}")
    else:
        logger.warning(f"Job with ID: {id} not found")
    return job
