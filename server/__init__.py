# client/__init__.py
from .server import app  # Assuming your FastAPI app is in main.py

# Export the app instance
__all__ = ['app']