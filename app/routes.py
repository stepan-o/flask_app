"""Application routes (views).

This module defines a simple blueprint with a homepage at `/` that renders
an HTML template, and a JSON health endpoint at `/api/health`.
Blueprints let you split your app into modular route groups and register
them on the main Flask app in `app.__init__.register_routes`.
"""

from flask import Blueprint, jsonify, render_template

# Create a blueprint to group related routes under a common namespace.
# The first argument is the blueprint name; `__name__` helps Flask locate
# resources relative to this module if needed.
bp = Blueprint("main", __name__)


@bp.get("/")
def index():
    """Render the homepage HTML template.

    Returns:
        A rendered `index.html` template.
    """
    return render_template("index.html")


@bp.get("/api/health")
def health():
    """Return a basic health/info JSON payload.

    Using `jsonify` ensures a proper `application/json` response with the
    appropriate status code (200 by default) and charset.
    """
    return jsonify({
        "message": "Hello, Flask!",
        "status": "ok"
    })
