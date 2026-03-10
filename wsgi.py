"""WSGI entry point for Gunicorn.

Usage (production):
    gunicorn wsgi:application --bind 0.0.0.0:8000 --workers 4

Usage (development):
    flask --app wsgi:application run --debug
"""

import os

from app import create_app

application = create_app(os.environ.get("FLASK_ENV", "production"))

if __name__ == "__main__":
    application.run()
