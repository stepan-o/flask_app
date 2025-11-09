# Flask App - Basic Project Structure

This repository contains a minimal Flask app scaffold using the application factory pattern. It assumes you manage your virtual environment with `uv` and that a `.venv` already exists (created via `uv venv`).

## Quick start

1. Verify `uv` is using your local `.venv` (Option 1: print interpreter path):

```bash
uv run python -c "import sys, pathlib; print(pathlib.Path(sys.executable).resolve())"
```

- Expected (macOS/Linux): ends with `/.venv/bin/python`
- Expected (Windows): ends with `\\.venv\\Scripts\\python.exe`

Alternatively, check the Python version (less definitive):

```bash
uv run python --version
# Or, using the `uv python` shim (note the `--` to pass args to Python):
uv python -- --version
# Or, after activating the venv directly:
python --version
```

See `Extra info` section for more details on how to verify the correct venv is active.

2. Install dependencies:

```bash
uv add Flask
```

3. Run the development server (two options):

- Directly via the provided `main.py` script:

```bash
uv run python main.py
```

- Or using Flask CLI with the factory pattern:

```bash
# macOS/Linux
export FLASK_APP="app:create_app"
uv run flask run --debug

# Windows (PowerShell)
$env:FLASK_APP = "app:create_app"
uv run flask run --debug
```

Then open http://127.0.0.1:5000/ in your browser. You should see a JSON message.

## Project layout

```
flask_app/
├── app/
│   ├── __init__.py        # application factory
│   └── routes.py          # example blueprint with a sample route
├── instance/
│   ├── .gitignore         # ignore secrets
│   └── config.py.example  # example instance config
├── config.py              # base/derived configuration classes
├── main.py                # dev entry point
├── wsgi.py                # WSGI entry (for gunicorn/uwsgi, etc.)
├── pyproject.toml         # project metadata and dependencies (uv-compatible)
└── README.md
```

## Configuration

- Default config loads from `config.Config`.
- If `instance/config.py` exists, it will override defaults. Copy `instance/config.py.example` to `instance/config.py` and edit as needed (e.g., secrets like `SECRET_KEY`).

## Notes

- This scaffold uses a blueprint named `main` and exposes a sample `/` endpoint returning JSON.
- For production, point your WSGI server to `wsgi:app`.


## How the `app` package works

The `app/` directory is the Python package that contains your Flask application code. Because it’s a package (it has an `__init__.py`), other modules can import it, e.g. `from app import create_app`.

### Application factory (`app/__init__.py`)
The core entry point is the `create_app` factory function:

```python
from flask import Flask

def create_app(config_object: str | None = None) -> Flask:
    app = Flask(__name__, instance_relative_config=True)

    # 1) Base config from project root's config.py
    app.config.from_object("config.Config")

    # 2) Optional override via import string (e.g., "config.DevelopmentConfig")
    if config_object:
        app.config.from_object(config_object)

    # 3) Instance-specific overrides from instance/config.py (if present)
    app.config.from_pyfile("config.py", silent=True)

    # Register routes/blueprints
    register_routes(app)
    return app
```

Key points:
- `instance_relative_config=True` makes Flask look for an `instance/` folder next to your project. This is where machine-specific and secret config lives, outside version control.
- Configuration load order (later overrides earlier):
  1) `config.Config` from `config.py`
  2) Optional `config_object` you pass in, e.g. `"config.DevelopmentConfig"`
  3) `instance/config.py` if it exists
- `register_routes(app)` defers blueprint imports to avoid side effects at import time and to keep the app factory clean.

### How it’s called
All entry points ultimately call `create_app()` and receive a configured `Flask` instance:

1) Development script (`main.py`):
```python
from app import create_app
app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
```
Run with:
```bash
uv run python main.py
```

2) Production/WGSI servers (`wsgi.py`):
```python
from app import create_app
app = create_app()  # WSGI callable named "app"
```
A WSGI server (e.g., gunicorn) loads `wsgi:app`:
```bash
gunicorn wsgi:app
```

3) Flask CLI (factory pattern):
```bash
export FLASK_APP="app:create_app"
uv run flask run --debug
```
The CLI imports the `app` package, finds the `create_app` factory, calls it, and runs the server.

### Routes via blueprints
Routes are organized in blueprints. Example (`app/routes.py`):
```python
from flask import Blueprint, jsonify
bp = Blueprint("main", __name__)

@bp.get("/")
def index():
    return jsonify({"message": "Hello, Flask!", "status": "ok"})
```
Registered in the factory (`app/__init__.py`):
```python
def register_routes(app: Flask) -> None:
    from .routes import bp as main_bp
    app.register_blueprint(main_bp)
```
After registration, visiting `http://127.0.0.1:5000/` returns the JSON above.

### Request lifecycle (what happens at runtime)
1. A request reaches the server (dev server, gunicorn, etc.).
2. Flask matches the URL/method against the app’s URL map (built from your blueprints).
3. The matching view function (e.g., `index`) executes.
4. The view returns a response value (string, dict/JSON, tuple, or `Response`).
5. Flask converts it to a proper `Response`, runs teardown/after-request handlers, and sends it back to the client.

### Why only `app` is packaged
`pyproject.toml` restricts package discovery to `app` and excludes `instance`:
```toml
[tool.setuptools.packages.find]
include = ["app*"]
exclude = ["instance*"]
```
This avoids the "Multiple top-level packages" error and ensures `instance/` is treated as runtime config, not distributable code.


## Extra info: uv-managed interpreter vs project `.venv`

When you run commands via `uv run`, the `sys.executable` path may point to uv’s managed interpreter cache (e.g., `~/.local/share/uv/python/...`) rather than a binary inside your project’s `.venv`. This is expected. What matters is where packages are resolved from (the active environment), not the interpreter binary location.

Use these quick checks to confirm your project’s `.venv` is the active environment:

- Check venv prefixes and site-packages path
  ```bash
  uv run python -c "import sys, sysconfig; print('prefix =', sys.prefix); print('base_prefix =', sys.base_prefix); print('venv_active =', sys.prefix != sys.base_prefix); print('purelib =', sysconfig.get_paths()['purelib'])"
  ```
  Expected: `venv_active = True` and `purelib` path inside `./.venv/.../site-packages`.

- Show where Flask is imported from
  ```bash
  uv run python -c "import flask, pathlib; print(pathlib.Path(flask.__file__).resolve())"
  ```
  Expected path inside `./.venv/.../site-packages/flask/`.

- Check pip install location
  ```bash
  uv run python -m pip --version
  ```
  Output should reference a path inside `.venv`.

If you specifically need the interpreter inside `.venv` (so `sys.executable` points there), run it directly or pin it in uv:

- Direct:
  ```bash
  ./.venv/bin/python --version
  ```
  (Windows PowerShell)
  ```powershell
  .venv\Scripts\python.exe --version
  ```

- With uv, pin the interpreter:
  ```bash
  uv run --python ./.venv/bin/python -c "import sys, pathlib; print(pathlib.Path(sys.executable).resolve())"
  ```
  (Windows)
  ```powershell
  uv run --python .venv\Scripts\python.exe -c "import sys, pathlib; print(__import__('pathlib').Path(__import__('sys').executable).resolve())"
  ```
