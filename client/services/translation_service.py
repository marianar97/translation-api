import asyncio
from ..logger_config import logger
import requests
from ..models import JobResponse, Status, TranslationRequest
from .webhook_service import WebhookService


class TranslationService:
    BASE_URL = "http://localhost:8000/translations/status/"

    @staticmethod
    async def create_translation(request: TranslationRequest) -> JobResponse:
        logger.info("Creating translation for request: %s", request)
        try:
            response = requests.post(
                f"{TranslationService.BASE_URL}",
                json=request.model_dump(),
                timeout=2,
                headers={"Content-Type": "application/json"},
            )
            response.raise_for_status()
            logger.info("Translation job created with response: %s", response.json())
        except requests.RequestException as e:
            logger.error(
                "Failed to create translation job for request: %s with error: %s",
                request,
                e,
            )
            raise
        return JobResponse(**response.json())

    @staticmethod
    async def get_job(job_id: str) -> JobResponse:
        try:
            response = requests.get(
                f"{TranslationService.BASE_URL}{job_id}",
                timeout=2,
                headers={"Content-Type": "application/json"},
            )
            response.raise_for_status()
            logger.info("Fetched job details for job ID: %s", job_id)
        except requests.RequestException as e:
            logger.error("Failed to fetch job with ID: %s with error: %s", job_id, e)
            raise
        return JobResponse(**response.json())

    @staticmethod
    async def monitor_job_status(job: JobResponse):
        logger.info("Starting to monitor job status for job ID: %s", job.id)
        while True:
            try:
                job = await TranslationService.get_job(job.id)
                current_status = job.status

                if current_status in [Status.COMPLETED, Status.ERROR]:
                    logger.info(
                        "Job ID %s completed with status: %s", job.id, current_status
                    )
                    await WebhookService.send_webhook(job)
                    return
                await asyncio.sleep(1)
            except Exception as e:
                logger.error(
                    "Error while monitoring job status for job ID %s: %s", job.id, e
                )
                raise
