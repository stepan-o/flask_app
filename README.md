# Flask App - Basic Project Structure

Minimal Flask app scaffold using the application factory pattern. Works with `uv` and a local `.venv`.

## Quick start

1) Install dependencies
```bash
uv sync
```

2) Run the development server (pick one)
- Script:
```bash
uv run python main.py
```
- Flask CLI (factory):
```bash
# macOS/Linux
export FLASK_APP="app:create_app"
uv run flask run --debug

# Windows (PowerShell)
$env:FLASK_APP = "app:create_app"
uv run flask run --debug
```

Open http://127.0.0.1:5000/ → HTML homepage.
JSON health: http://127.0.0.1:5000/api/health

Tip: For production‑like serving locally:
```bash
uv run -s serve   # gunicorn -c gunicorn.conf.py wsgi:app
```

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

- Base config: `config.Config`.
- Optional machine/secret overrides: copy `instance/config.py.example` → `instance/config.py` and edit (e.g., `SECRET_KEY`).
- Packaging: templates and static assets are included in built wheels/sdists so `pip install .` deployments work out of the box.

---

# Extras / Appendix

The following sections provide deeper detail and optional tooling. They’re not required for a quick local run.

## A1. uv‑managed interpreter vs project `.venv`

When you run commands via `uv run`, `sys.executable` may point to uv’s managed interpreter cache (e.g., `~/.local/share/uv/python/...`) rather than a binary inside your project’s `.venv`. This is expected. What matters is where packages are resolved from (the active environment), not the interpreter binary location.

Quick checks:

- Check venv prefixes and site‑packages path
  ```bash
  # In a venv, prefix != base_prefix; purelib should live under .venv
  uv run python -c "import sys, sysconfig; \
print('prefix     =', sys.prefix); \
print('base_prefix=', sys.base_prefix); \
print('venv_active=', sys.prefix != sys.base_prefix); \
print('purelib    =', sysconfig.get_paths()['purelib'])"
  ```

- Show where Flask is imported from
  ```bash
  uv run python -c "import flask, pathlib; print(pathlib.Path(flask.__file__).resolve())"
  # Expect: .../.venv/.../site-packages/flask/__init__.py
  ```

- Check pip install location
  ```bash
  uv run python -m pip --version
  # Expect install location under .venv
  ```

If you specifically need the interpreter inside `.venv`, run it directly or pin it in uv:

- Direct (POSIX): `./.venv/bin/python --version`
- Direct (Windows): `.venv\Scripts\python.exe --version`
- uv (POSIX): `uv run --python ./.venv/bin/python -c "import sys, pathlib; print(pathlib.Path(sys.executable).resolve())"`
- uv (Windows): `uv run --python .venv\Scripts\python.exe -c "import sys, pathlib; print(__import__('pathlib').Path(__import__('sys').executable).resolve())"`

## A2. Running with Gunicorn (production)

Already included:
- `wsgi.py` exposing `app`
- `gunicorn` dependency and `gunicorn.conf.py`
- uv script aliases (`serve`, `serve-dev`)

Quick start:
```bash
uv sync
uv run -s serve
# ≈ uv run gunicorn -c gunicorn.conf.py wsgi:app
```
Dev auto‑reload (not for prod):
```bash
uv run -s serve-dev
```
Tuning via env (or `.env` locally):
```bash
export GUNICORN_BIND=0.0.0.0:8000
export GUNICORN_WORKERS=5
export GUNICORN_THREADS=2
export GUNICORN_TIMEOUT=60
export GUNICORN_LOGLEVEL=info
uv run -s serve
```
Windows: Gunicorn targets UNIX; use WSL or an alternative like Waitress.

## A3. Using the Makefile

Run `make help` for all targets. Common ones:
```bash
make venv         # create .venv (uv)
make sync         # install deps
make run          # dev server via main.py
make flask-run    # dev via Flask CLI
make serve        # gunicorn
make serve-dev    # gunicorn --reload
make routes       # list routes
make shell        # Flask shell
make check-venv   # verify active env/site-packages
make add PKG=...  # add a dependency
make clean        # remove caches/artifacts
```

## A4. Deploying to Render

Use the included `render.yaml` (Blueprint):
- Build:
  ```
  pip install --upgrade pip
  pip install .
  ```
- Start:
  ```
  gunicorn -c gunicorn.conf.py wsgi:app
  ```
- Health check: `/api/health`
- `gunicorn.conf.py` auto‑binds to `0.0.0.0:$PORT` when `PORT` is set by the platform.

Important: Do NOT use `app:app` as the Gunicorn target. Our WSGI callable lives in `wsgi.py`.
- Correct: `wsgi:app`
- Incorrect (will fail with "module 'app' has no attribute 'app'"): `app:app`

If you configure the service manually in the Render dashboard (without the blueprint), set:
- Build Command: `pip install --upgrade pip && pip install .`
- Start Command: `gunicorn -c gunicorn.conf.py wsgi:app`
- Health Check Path: `/api/health`

## A5. Auto‑formatting, linting, and CI

- Local:
  ```bash
  make hooks
  make format
  make format-check
  ```
- CI (`.github/workflows/ci.yml`) runs pre‑commit, a smoke app import, and a Gunicorn config import.
- Auto‑format workflow (`.github/workflows/auto-format.yml`) can push fixes back to your branch.

## A6. Contributing & commit style

Use small, focused commits; Conventional Commits are recommended:
- `feat(scope): ...`, `fix(scope): ...`, `docs(scope): ...`, `build(scope): ...`, `chore(scope): ...`

## A7. How the `app` package works (overview)

Factory pattern in `app/__init__.py`, blueprint in `app/routes.py`.
- `/` renders HTML via `templates/index.html`
- `/api/health` returns JSON

See source files for inline docstrings/comments if you want a deeper dive.
