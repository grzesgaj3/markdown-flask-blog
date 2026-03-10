"""Configuration classes for the Flask blog."""

import os


class Config:
    """Base configuration."""

    SECRET_KEY = os.environ.get("SECRET_KEY", "change-me-in-production")
    POSTS_DIR = os.environ.get(
        "POSTS_DIR",
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "posts"),
    )
    POSTS_PER_PAGE = int(os.environ.get("POSTS_PER_PAGE", "10"))


class DevelopmentConfig(Config):
    """Development configuration."""

    DEBUG = True


class ProductionConfig(Config):
    """Production configuration."""

    DEBUG = False


class TestingConfig(Config):
    """Testing configuration."""

    TESTING = True
    DEBUG = True


config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig,
}
