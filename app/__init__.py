"""Flask application factory."""

import os

from flask import Flask

from config import config


def create_app(env: str = None) -> Flask:
    """Create and configure the Flask application."""
    env = env or os.environ.get("FLASK_ENV", "default")
    app = Flask(__name__, template_folder="templates", static_folder="../static")
    app.config.from_object(config[env])

    from .routes import bp
    app.register_blueprint(bp)

    return app
