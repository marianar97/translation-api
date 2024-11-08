from enum import Enum
import datetime
from pydantic import BaseModel, Field, field_validator


class Status(str, Enum):
    PENDING = "pending"
    ERROR = "error"
    COMPLETED = "completed"


class JobResponse(BaseModel):
    id: str
    webhook_url: str
    created_at: datetime.datetime
    duration: float
    status: str


class TranslationRequest(BaseModel):
    duration: float = Field(description="configurable delay in seconds")
    webhook_url: str = Field(
        description="url endpoint to notify once the translation is completed"
    )

    @field_validator("webhook_url")
    def validate_webhook_url(cls, v):
        if not v.startswith(("http://", "https://")):
            raise ValueError("webhook_url must be a valid HTTP or HTTPS URL")
        return v

    @field_validator("duration")
    def check_duration_positive(cls, value):
        if value <= 0:
            raise ValueError("duration must be greater than 0")
        return value

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "duration": 30.5,
                    "webhook_url": "https://webhook.site/94070b61-3ca5-4a17-8fc0-db7b8a8c1c8c",
                }
            ]
        }
    }
