"""
Gunicorn configuration for running this Flask application in production.

You can override most values via environment variables without editing this file.
Common overrides:
- PORT (Render/Heroku et al.) — if set, bind will auto-configure to 0.0.0.0:$PORT
- GUNICORN_BIND (default: 127.0.0.1:8000)
- GUNICORN_WORKERS (default: 2*CPU + 1)
- GUNICORN_THREADS (default: 1)
- GUNICORN_TIMEOUT (default: 30)
- GUNICORN_KEEPALIVE (default: 2)
- GUNICORN_LOGLEVEL (default: info)
- GUNICORN_WORKER_CLASS (default: sync)

Run examples:
    uv run gunicorn -c gunicorn.conf.py wsgi:app
    uv run -s serve        # uses [tool.uv.scripts] alias
"""

from __future__ import annotations

import multiprocessing
import os

# Load environment variables from a local .env file if present (for local/dev)
# In production (e.g., Render), the platform provides environment variables; this
# call is a no-op if .env does not exist.
try:
    from dotenv import load_dotenv  # type: ignore
except ImportError:
    # python-dotenv not installed; in production, environment variables should be
    # provided by the platform. It's safe to continue without loading a .env file.
    load_dotenv = None  # type: ignore[assignment]
else:
    # Load environment variables from a local .env file if present.
    load_dotenv()

# Network binding
# Priority:
# 1) If PORT is provided by the platform (e.g., Render), bind to 0.0.0.0:$PORT
# 2) Else, use GUNICORN_BIND if provided
# 3) Else, fall back to 127.0.0.1:8000 for local dev
_port = os.getenv("PORT")
_bind_env = os.getenv("GUNICORN_BIND")
if _port:
    bind = f"0.0.0.0:{_port}"
else:
    bind = _bind_env or "127.0.0.1:8000"

# Worker processes: recommended formula 2*CPU + 1 for sync workers.
workers = int(os.getenv("GUNICORN_WORKERS", str(multiprocessing.cpu_count() * 2 + 1)))

# Optional threads per worker (useful for I/O heavy apps). Keep modest if using sync workers.
threads = int(os.getenv("GUNICORN_THREADS", "1"))

# Worker class: 'sync' (default), or 'gthread', 'gevent', etc.
worker_class = os.getenv("GUNICORN_WORKER_CLASS", "sync")

# Timeouts and connection keepalive
timeout = int(os.getenv("GUNICORN_TIMEOUT", "30"))
keepalive = int(os.getenv("GUNICORN_KEEPALIVE", "2"))

# Logging: '-' means stdout/stderr (12-factor friendly)
loglevel = os.getenv("GUNICORN_LOGLEVEL", "info")
accesslog = "-"
errorlog = "-"

# pidfile = "gunicorn.pid"  # Uncomment to write a PID file
# capture_output = True      # Capture print() to error log

# NOTE:
# - In development you can add '--reload' on the CLI instead of enabling it here:
#     uv run gunicorn --reload --bind 127.0.0.1:8000 wsgi:app
