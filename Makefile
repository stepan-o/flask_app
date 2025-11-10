# Makefile for managing the Flask + uv project
#
# Usage examples:
#   make help           # list targets
#   make venv           # create .venv using uv (if missing)
#   make sync           # install/sync dependencies from pyproject/uv.lock
#   make run            # run development server via main.py
#   make flask-run      # run via Flask CLI (debug)
#   make serve          # run with Gunicorn (production-like)
#   make serve-dev      # run Gunicorn with --reload (dev)
#   make routes         # list Flask routes
#   make shell          # open Flask shell
#   make check-venv     # verify the active environment is .venv
#   make add PKG=name   # add a dependency with uv
#   make clean          # remove caches/artifacts

# Defaults (override on the command line if needed)
FLASK_APP ?= app:create_app
BIND ?= 127.0.0.1:8000
PY ?= python

# Internal helper for uv execution
UV := uv

.DEFAULT_GOAL := help
.PHONY: help venv sync add run flask-run serve serve-dev routes shell check-venv where-flask pip-show clean env hooks format format-check

help: ## Show this help
	@awk 'BEGIN {FS = ":.*##"} /^[a-zA-Z0-9_.-]+:.*##/ {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

venv: ## Create a local .venv using uv (no-op if it exists)
	@if [ ! -d .venv ]; then $(UV) venv; else echo ".venv already exists"; fi

sync: ## Install/sync dependencies from pyproject/uv.lock
	$(UV) sync

add: ## Add a dependency: make add PKG=<name>[==version]
	@test -n "$(PKG)" || (echo "Usage: make add PKG=<name>[==version]" && false)
	$(UV) add $(PKG)

run: ## Start development server via main.py
	$(UV) run $(PY) main.py

flask-run: ## Start development server via Flask CLI (factory pattern)
	FLASK_APP=$(FLASK_APP) $(UV) run flask run --debug --host $(word 1,$(subst :, ,$(BIND))) --port $(word 2,$(subst :, ,$(BIND)))

serve: ## Run with Gunicorn using gunicorn.conf.py (production-like)
	$(UV) run -s serve

serve-dev: ## Run Gunicorn with auto-reload for development
	$(UV) run -s serve-dev

routes: ## List Flask routes (requires FLASK_APP)
	FLASK_APP=$(FLASK_APP) $(UV) run flask routes

shell: ## Open Flask shell (requires FLASK_APP)
	FLASK_APP=$(FLASK_APP) $(UV) run flask shell

check-venv: ## Verify active environment and site-packages come from .venv
	$(UV) run $(PY) -c "import sys, sysconfig, pathlib; print('exe    =', pathlib.Path(sys.executable).resolve()); print('prefix =', sys.prefix); print('base   =', sys.base_prefix); print('venv   =', sys.prefix != sys.base_prefix); print('purelib=', sysconfig.get_paths()['purelib'])"

where-flask: ## Show the installed path of Flask (should be under .venv)
	$(UV) run $(PY) -c "import flask, pathlib; print(pathlib.Path(flask.__file__).resolve())"

pip-show: ## Show pip version and install location
	$(UV) run $(PY) -m pip --version

clean: ## Remove Python caches and common artifacts
	rm -rf __pycache__ */__pycache__ .pytest_cache .coverage .coverage.* htmlcov build dist *.egg-info

env: ## Create .env from .env.example if missing
	@if [ ! -f .env ]; then cp .env.example .env && echo "Created .env from .env.example"; else echo ".env already exists"; fi

hooks: ## Install local pre-commit hooks
	uvx pre-commit install
	uvx pre-commit install-hooks

format: ## Auto-fix formatting/lint via pre-commit on all files
	uvx pre-commit run --all-files || true

format-check: ## Check formatting/lint (CI-like); fails if changes would be made
	uvx pre-commit run --all-files --show-diff-on-failure
