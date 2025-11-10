"""Application configuration classes.

These classes centralize configuration for different environments. The factory
(`create_app`) loads `Config` by default, then may override with a specific
class (e.g., `DevelopmentConfig`) and finally with values from
`instance/config.py`.

Use environment variables to avoid hardcoding secrets or environment-specific
values. The `instance/` config file is ignored if absent and should not be
committed to VCS.
"""

import os


class Config:
    """Base configuration shared by all environments.

    Attributes:
        SECRET_KEY: Used by Flask to sign session cookies and CSRF tokens.
            Defaults to a dev value; override via the `SECRET_KEY` env var.
        DEBUG: Enables debugger and auto-reload. Intended for development only.
            Defaults based on the `FLASK_DEBUG` env var.
        TESTING: Puts Flask in testing mode (propagate exceptions, etc.).
    """

    # Secret for sessions/CSRF. In production, be sure to set SECRET_KEY env.
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-me")
    # Enable debug based on env var; `flask run --debug` also toggles debugger.
    DEBUG = os.environ.get("FLASK_DEBUG", "0") == "1"
    # Global testing flag (used by Flask and some extensions)
    TESTING = False


class DevelopmentConfig(Config):
    """Settings tailored for local development."""

    DEBUG = True


class TestingConfig(Config):
    """Settings used by test runs (pytest, etc.)."""

    TESTING = True
    DEBUG = True


class ProductionConfig(Config):
    """Production-safe defaults (debug off)."""

    DEBUG = False
