"""
Development runner for the Flask app.

- Imports the application factory (`create_app`) from the `app` package.
- Builds a Flask application instance for the current environment.
- When executed directly (not imported), starts Flask's built-in development server.

Tip: For production, use a real WSGI server and the `wsgi.py` entry instead.
"""

from app import create_app

# Build the Flask application using the factory pattern. You can pass a
# config import string here to override, e.g.:
#   create_app("config.DevelopmentConfig")
# If omitted, base config + optional instance config will be used.
app = create_app()


if __name__ == "__main__":
    # Development entry point: run Flask's reloader/debug server.
    # NOTE: Do not use this in production; prefer gunicorn/uwsgi via wsgi.py
    app.run(debug=True)
