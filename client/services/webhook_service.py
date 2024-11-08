import asyncio
import os
from dotenv import load_dotenv
from ..logger_config import logger
import requests
from ..models import JobResponse

load_dotenv()

class WebhookService:
    MAX_RETRIES = int(os.getenv('MAX_RETRIES'))
    RETRY_DELAY = int(os.getenv('RETRY_DELAY'))
    
    @staticmethod
    async def send_webhook(job: JobResponse) -> bool:
        payload = {
            "job_id": job.id,
            "status": job.status,
            "created_at": str(job.created_at),
            "event_type": "translation.status_update",
        }

        for attempt in range(WebhookService.MAX_RETRIES):
            try:
                logger.info(
                    "Attempt %d to send webhook for job ID: %s", attempt + 1, job.id
                )
                response = requests.post(
                    job.webhook_url,
                    json=payload,
                    timeout=5,
                    headers={"Content-Type": "application/json"},
                )
                if response.ok:
                    logger.info("Successfully sent webhook for job ID: %s", job.id)
                    return True

            except requests.RequestException as e:
                logger.error(
                    "Webhook attempt %d failed for job ID: %s with error: %s",
                    attempt + 1,
                    job.id,
                    e,
                )

            logger.info("Retrying webhook for job ID: %s after delay", job.id)
            await asyncio.sleep(WebhookService.RETRY_DELAY * (2**attempt))

        logger.warning(
            "Failed to send webhook after %d attempts for job ID: %s",
            WebhookService.MAX_RETRIES,
            job.id,
        )
        return False
