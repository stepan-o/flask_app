"""WSGI entry point for production servers.

WSGI servers (e.g., gunicorn, uWSGI, mod_wsgi) import this module and look for
an object named `app` that conforms to the WSGI callable interface. We build it
via the application factory to keep configuration consistent with `main.py` and
Flask CLI usage.

Example (gunicorn):
    gunicorn wsgi:app
"""

from app import create_app

# The WSGI callable expected by servers; do not enable debug here.
app = create_app()
