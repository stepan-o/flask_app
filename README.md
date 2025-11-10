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
uv sync
```

Optional (local dev): copy environment template and adjust values if needed
(e.g., bind address, workers). The app will auto-load `.env` when present.

```bash
cp .env.example .env
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

Then open http://127.0.0.1:5000/ in your browser. You should see the HTML homepage.
For a JSON response, visit the health endpoint at http://127.0.0.1:5000/api/health.

## Project layout

```
flask_app/
├── app/
│   ├── __init__.py              # application factory
│   ├── routes.py                # blueprint with HTML homepage + /api/health JSON
│   ├── templates/
│   │   ├── base.html
│   │   └── index.html
│   └── static/
│       ├── css/styles.css
│       └── js/main.js
├── instance/
│   ├── .gitignore               # ignore secrets
│   └── config.py.example        # example instance config
├── config.py                    # base/derived configuration classes
├── main.py                      # dev entry point
├── wsgi.py                      # WSGI entry (for Gunicorn/uWSGI)
├── gunicorn.conf.py             # Gunicorn configuration (env-driven)
├── Makefile                     # common tasks (uv, flask, gunicorn)
├── pyproject.toml               # project metadata and dependencies (uv-compatible)
├── uv.lock                      # lockfile for reproducible installs
├── render.yaml                  # Render.com blueprint
├── .env.example                 # local env template (optional)
└── README.md
```

## Configuration

- Default config loads from `config.Config`.
- If `instance/config.py` exists, it will override defaults. Copy `instance/config.py.example` to `instance/config.py` and edit as needed (e.g., secrets like `SECRET_KEY`).

## Notes

- This scaffold uses a blueprint named `main`. The `/` endpoint renders an HTML homepage, and `/api/health` returns JSON.
- For production, point your WSGI server to `wsgi:app`.


## How the `app` package works (overview)

This project uses the application factory pattern in `app/__init__.py` and a blueprint in `app/routes.py`. The `/` route renders an HTML homepage; `/api/health` returns JSON.

For a detailed walkthrough of how the factory, blueprints, and request lifecycle work, see: Appendix — How the `app` package works.


## Extra info: uv-managed interpreter vs project `.venv`

When you run commands via `uv run`, the `sys.executable` path may point to uv’s managed interpreter cache (e.g., `~/.local/share/uv/python/...`) rather than a binary inside your project’s `.venv`. This is expected. What matters is where packages are resolved from (the active environment), not the interpreter binary location.

Below are quick checks with inline comments showing what each line means and what to look for.

- Check venv prefixes and site-packages path
  ```bash
  # Prints the active environment prefix (venv) and the base interpreter prefix.
  # In a virtualenv, these differ; in system Python, they are the same.
  uv run python -c "import sys, sysconfig; \
print('prefix     =', sys.prefix); \
print('base_prefix=', sys.base_prefix); \
print('venv_active=', sys.prefix != sys.base_prefix); \
print('purelib    =', sysconfig.get_paths()['purelib'])"
  # Expected:
  # - venv_active = True
  # - purelib points inside your project: ./\.venv/.../site-packages
  ```

- Show where Flask is imported from
  ```bash
  # Resolves the installed location of the Flask package.
  # The printed path should live under your project's .venv.
  uv run python -c "import flask, pathlib; print(pathlib.Path(flask.__file__).resolve())"
  # Expected: .../your-project/.venv/.../site-packages/flask/__init__.py
  ```

- Check pip install location
  ```bash
  # Shows which pip is running and where it installs packages.
  # The location in the output should be a path inside .venv.
  uv run python -m pip --version
  ```

If you specifically need the interpreter inside `.venv` (so `sys.executable` points there), run it directly or pin it in uv:

- Direct:
  ```bash
  # POSIX (macOS/Linux): use the venv's python binary directly
  ./.venv/bin/python --version
  ```
  (Windows PowerShell)
  ```powershell
  # Windows: use the venv's python.exe directly
  .venv\Scripts\python.exe --version
  ```

- With uv, pin the interpreter:
  ```bash
  # Force uv to use the interpreter located in your .venv
  uv run --python ./.venv/bin/python -c "import sys, pathlib; print(pathlib.Path(sys.executable).resolve())"
  ```
  (Windows)
  ```powershell
  # Force uv to use the .venv\Scripts\python.exe explicitly
  uv run --python .venv\Scripts\python.exe -c "import sys, pathlib; print(__import__('pathlib').Path(__import__('sys').executable).resolve())"
  ```


## Running with Gunicorn (production)

Gunicorn is a production WSGI HTTP server for UNIX. This project already includes:
- `wsgi.py` exposing a WSGI callable `app`
- `gunicorn` listed as a dependency in `pyproject.toml`
- A sample `gunicorn.conf.py` with sensible defaults
- uv script aliases for convenience in `[tool.uv.scripts]`

### Install dependencies (sync)
If you just pulled these changes, make sure your env is up to date:
```bash
uv sync
```

### Quick start (recommended)
Use the uv script alias to run Gunicorn with the included config:
```bash
uv run -s serve
```
This is equivalent to:
```bash
uv run gunicorn -c gunicorn.conf.py wsgi:app
```

- Default bind: `127.0.0.1:8000`
- Default workers: `2 * CPU + 1`
- Logs to stdout/stderr

Open http://127.0.0.1:8000/ and you should see the HTML homepage at `/`.

### Development convenience
Auto-reload on code changes (not for production):
```bash
uv run -s serve-dev
# or
uv run gunicorn --reload --bind 127.0.0.1:8000 wsgi:app
```

### Tuning via environment variables
You can override settings without editing the config file:
```bash
export GUNICORN_BIND=0.0.0.0:8000
export GUNICORN_WORKERS=5
export GUNICORN_THREADS=2
export GUNICORN_TIMEOUT=60
export GUNICORN_LOGLEVEL=debug
uv run -s serve
```
Or put these values into a local `.env` file (ignored by Git). `gunicorn.conf.py` will auto-load `.env` for local/dev:
```dotenv
# .env (local dev)
GUNICORN_BIND=127.0.0.1:8000
GUNICORN_WORKERS=3
GUNICORN_THREADS=1
GUNICORN_TIMEOUT=30
GUNICORN_LOGLEVEL=info
# SECRET_KEY and other app settings can go here too
```
Common guidance:
- Workers: start with `2 * CPU + 1` for `sync` workers, then adjust under real load.
- Use `GUNICORN_WORKER_CLASS=gthread` with `threads>1` for I/O-heavy apps if needed.

### Windows note
Gunicorn targets UNIX. On Windows, use WSL or an alternative server (e.g., Waitress):
```bash
uv add waitress
uv run waitress-serve --listen=127.0.0.1:8000 wsgi:app
```

### Behind a reverse proxy
In production, run Gunicorn behind a reverse proxy (e.g., Nginx) that terminates TLS and forwards to `127.0.0.1:8000`. Your `/` endpoint serves as a simple health check.


## Using the Makefile

Common project tasks are available via `make` (wrappers around `uv` and Flask/Gunicorn). Run `make help` to see all targets.

Examples:

```bash
# One-time setup
make venv           # create .venv with uv (no-op if exists)
make sync           # install/sync dependencies from pyproject/uv.lock

# Development
make run            # run dev server via main.py
make flask-run      # run via Flask CLI (factory), debug + reload

# Production-like
make serve          # run Gunicorn with gunicorn.conf.py
make serve-dev      # Gunicorn with --reload (dev)

# Utilities
make routes         # list Flask routes
make shell          # open a Flask shell
make check-venv     # verify .venv is the active environment
make add PKG=name   # add a dependency, e.g., make add PKG=flask-cors
make clean          # remove caches and build artifacts
```

Notes:
- Targets assume `uv` is installed and the current directory is the project root.
- `FLASK_APP` defaults to `app:create_app`. Override temporarily with `FLASK_APP=... make flask-run` if needed.
- `BIND` defaults to `127.0.0.1:8000` for CLI where applicable; override like `BIND=0.0.0.0:8000 make flask-run`.


## Contributing & commit style

This repo uses small, focused commits and Conventional Commits for clarity.

- Commit message format examples:
  - `feat(templates): add base layout and homepage`
  - `build(deps): add gunicorn and uv scripts; update uv.lock`
  - `docs(readme): document frontend and gunicorn usage`
- Keep one concern per commit (code, docs, tooling separated where practical).
- Include `BREAKING CHANGE:` in the body if behavior changes in a non‑backward‑compatible way.

### Pre‑commit hooks (format/lint)
Install pre‑commit locally to keep changes tidy before committing:

```bash
# Install hooks (no global python needed; uses uv's tool runner)
uvx pre-commit install
uvx pre-commit install-hooks

# Run on all files (optional, CI does this too)
uvx pre-commit run --all-files
```

The configured hooks run Black (format), isort (imports), Ruff (lint), and some basic whitespace/EOF fixers. CI will run these hooks on every push/PR.

### CI
GitHub Actions workflow `.github/workflows/ci.yml` performs:
- uv environment setup + `uv sync`
- pre‑commit hooks on the whole tree
- A Python smoke test that imports the app and builds the Flask instance
- A Gunicorn config import check

### Optional: rename default branch to `main`
If you want to switch from `master` to `main`, run:

```bash
git branch -m master main
git push -u origin main
# After updating repo settings to use main as default:
git push origin --delete master
```

Update branch protection rules and CI settings accordingly if you use them.


## Deploying to Render

Render expects your web service to listen on the TCP port provided in the `PORT` environment variable and to bind to `0.0.0.0`. This repo is pre-configured to make that seamless.

### Easiest: use the provided render.yaml
A `render.yaml` is included at the repo root. On Render, choose New → Blueprint and point it to this repository.
- Build Command (from render.yaml):
  ```
  pip install --upgrade pip
  pip install .
  ```
- Start Command (from render.yaml):
  ```
  gunicorn -c gunicorn.conf.py wsgi:app
  ```
- Health check: `/api/health`
- Environment: `SECRET_KEY` is generated; you can add optional `GUNICORN_*` vars.

The included `gunicorn.conf.py` auto-binds to `0.0.0.0:$PORT` when `PORT` is set by the platform, so you don’t need to hardcode the port.

### Alternative: configure a Render Web Service manually
If you prefer the UI without `render.yaml`:
- Build Command: `pip install .`
- Start Command: `gunicorn -c gunicorn.conf.py wsgi:app`
- Health Check Path: `/api/health`
- Environment variables:
  - `SECRET_KEY` — set a secure value
  - Optional tuning: `GUNICORN_WORKERS`, `GUNICORN_THREADS`, `GUNICORN_TIMEOUT`, `GUNICORN_LOGLEVEL`

Notes:
- You do not need to use `uv` on Render; standard `pip install .` works because dependencies are declared in `pyproject.toml` and packaged as `app`.
- If you choose to use `uv` on Render, install it in the Build Command and run `uv sync`, then your Start Command could be `uv run gunicorn -c gunicorn.conf.py wsgi:app`. The provided `render.yaml` uses the simpler `pip` approach for broad compatibility.
