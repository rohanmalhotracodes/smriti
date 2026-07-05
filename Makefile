# Smriti — dev & demo shortcuts.
#
# Quick start:
#   make setup        — venv + backend deps + frontend deps + .env
#   make db           — start PostgreSQL (Docker)
#   make dev          — run backend (:8000) + frontend (:5173) together
#   make seed-india   — seed Delhi NCR dispatch data into the DB
#   make seed-memory  — seed 40+ historical memories into Cognee Cloud
#   make demo         — full demo stack (db + seed + dev servers)

COMPOSE := docker compose -p smriti
PY      := .venv/bin/python
PIP     := .venv/bin/pip

.PHONY: setup db dev backend frontend seed-india seed-memory demo \
        up docker-demo down clean logs ps rebuild

setup:
	python3 -m venv .venv || true
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	cd frontend && npm install
	@test -f .env || cp .env.example .env
	@echo "✅ Setup complete. Edit .env with your COGNEE_API_KEY, then: make db && make dev"

db:
	$(COMPOSE) up -d postgres

backend:
	$(PY) -m uvicorn backend.api.main:app --reload --port 8000

frontend:
	cd frontend && npm run dev

dev:
	@trap 'kill 0' INT; \
	$(PY) -m uvicorn backend.api.main:app --reload --port 8000 & \
	(cd frontend && npm run dev) & \
	wait

seed-india:
	curl -s -X POST localhost:8000/api/v1/demo/seed-india | $(PY) -m json.tool || \
	$(PY) -m backend.database.seeds.seed_data

seed-memory:
	curl -s -X POST localhost:8000/api/v1/memory/seed-india --max-time 600 | $(PY) -m json.tool

demo: db
	@sleep 2
	@$(MAKE) dev

# ── Docker targets (single-container stack) ───────────────────────────
up:
	$(COMPOSE) up --build --remove-orphans

docker-demo:
	IS_DEMO=true $(COMPOSE) up --build --remove-orphans

down:
	$(COMPOSE) down --remove-orphans

clean:
	$(COMPOSE) down -v --remove-orphans

logs:
	$(COMPOSE) logs -f app

ps:
	$(COMPOSE) ps

rebuild:
	$(COMPOSE) build --no-cache app
