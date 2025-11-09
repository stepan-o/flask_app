"""Flask application package.

This module exposes the application factory `create_app`, which builds and
configures a Flask app instance. The factory pattern lets you configure the
application differently for development, testing, and production, and avoids
side effects at import time.

Configuration sources (later overrides earlier):
1) `config.Config`              — base defaults from project `config.py`
2) optional `config_object`     — import string like "config.DevelopmentConfig"
3) `instance/config.py`         — machine/secret overrides (ignored if missing)

Blueprints (routes) are registered via `register_routes` to keep imports local
and avoid circular dependencies during app construction.
"""

from flask import Flask


def create_app(config_object: str | None = None) -> Flask:
    """Application factory for the Flask app.

    Args:
        config_object: Optional import string pointing to a config class
            (e.g., "config.DevelopmentConfig"). When provided, it overrides
            the base `Config` values.

    Returns:
        A fully configured `Flask` application instance.
    """
    # `instance_relative_config=True` tells Flask that configuration files
    # should be read from an `instance/` folder located next to the project
    # package. This folder is typically excluded from version control and is
    # safe for secrets (API keys, DB URIs, etc.).
    app = Flask(__name__, instance_relative_config=True)

    # 1) Load base/default configuration from project root's config.py
    app.config.from_object("config.Config")

    # 2) Optionally apply a specific configuration class via import string
    if config_object:
        app.config.from_object(config_object)

    # 3) Load instance-specific overrides from instance/config.py if present
    app.config.from_pyfile("config.py", silent=True)

    # Register blueprints / routes (kept in a separate function to avoid
    # importing blueprints at module import time).
    register_routes(app)

    return app


def register_routes(app: Flask) -> None:
    """Register all application blueprints on the given app.

    Keeping this in a separate function avoids importing blueprint modules
    before the app exists and reduces chances of circular imports.
    """
    # Local import to defer blueprint module loading until the app is created.
    from .routes import bp as main_bp

    app.register_blueprint(main_bp)
