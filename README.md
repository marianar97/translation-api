# FastAPI Translation Service

A robust FastAPI application that manages translation jobs with webhook notifications. This service provides an asynchronous API for submitting translation jobs, monitoring their status, and receiving webhook notifications upon completion.

## Features

- 🚀 Asynchronous job processing
- 📊 Job status monitoring
- 🔔 Webhook notifications with retry mechanism
- ⚡ FastAPI-powered REST API
- 🏗️ Modular and maintainable architecture

## Project Structure

```
client/
├── __init__.py   
├── client.py          # FastAPI application and routes
├── logger_config.py   # logging configuration
├── models.py        # Pydantic models and enums
├── requirements.txt    
└── services/
    ├── translation_service.py  # Translation-related operations
    └── webhook_service.py      # Webhook handling and retries
  
server/
├── __init__.py   
├── jobs.py          # Translation Job Class
├── models.py        # Pydantic models and enums
├── server.py        # FastAPI applications and routes
├── requirements.txt    
```

## Requirements

- Python 3.8+
- FastAPI
- Uvicorn
- Requests
- Pydantic

## Installation

1. Clone the repository:
```bash
git clone https://github.com/marianar97/TranslateAPIClientLibrary.git
cd TranslateAPIClientLibrary
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application
```bash
uvicorn server:app --host 0.0.0.0 --port 5000
```
in another terminal run

```bash
uvicorn client:app --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`, and you can access the interactive API documentation at `http://localhost:8000/docs`

## API Endpoints

### Create Translation Job

```http
POST /translations/job/
```

Request body:
```json
{
    "duration": 30.5,
    "webhook_url": "https://your-webhook-endpoint.com/callback"
}
```

Response:
```json
{
  "id": "97fabbb7-6f5c-49f0-964d-cf7feca5642c",
  "webhook_url": "https://your-webhook-endpoint.com/callback",
  "created_at": "2024-11-07T00:53:39.054062Z",
  "duration": 30.5,
  "status": "pending"
}
```

## Webhook Notifications

Upon job completion or error, the service will send a webhook notification to the specified URL with the following payload:

```json
{
  "job_id": "e39e4668-ea7a-4fea-af92-efd65200a256",
  "status": "completed",
  "created_at": "2024-11-07 00:39:06.562608+00:00",
  "event_type": "translation.status_update"
}
```

The webhook service includes:
- Maximum of 3 retry attempts
- Exponential backoff between retries
- 5-second timeout for each attempt

## Configuration

Key configuration values can be found in the .env file for easy configuration:

- `WebhookService`:
  - `MAX_RETRIES = 3`
  - `RETRY_DELAY = 5` (seconds)

- `TranslationService`:
  - `BASE_URL = "https://translation-api-backend.vercel.app/translations/status"`


## Error Handling

The service includes robust error handling for:
- Failed webhook deliveries
- Translation API communication issues
- Invalid requests
- Timeouts

## Integration Tests

```bash
pytest -vv -s --log-cli-level=INFO .\test_translation_integration.py    
```


