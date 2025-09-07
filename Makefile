.PHONY: help dev dev-backend dev-frontend install-backend install-frontend clean

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

dev: ## Start both frontend and backend in development mode
	@echo "Starting development environment..."
	@echo "Backend will run on http://localhost:8000"
	@echo "Frontend will run on http://localhost:3000"
	@echo ""
	@echo "Starting backend..."
	@cd backend && python -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt && uvicorn main:app --reload --port 8000 &
	@echo "Starting frontend..."
	@cd frontend && pnpm install && pnpm dev

dev-backend: ## Start only the backend in development mode
	@echo "Starting backend on http://localhost:8000"
	@cd backend && python -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt && uvicorn main:app --reload --port 8000

dev-frontend: ## Start only the frontend in development mode
	@echo "Starting frontend on http://localhost:3000"
	@cd frontend && pnpm install && pnpm dev

install-backend: ## Install backend dependencies
	@echo "Installing backend dependencies..."
	@cd backend && python -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt

install-frontend: ## Install frontend dependencies
	@echo "Installing frontend dependencies..."
	@cd frontend && pnpm install

install: install-backend install-frontend ## Install all dependencies

clean: ## Clean up generated files and dependencies
	@echo "Cleaning up..."
	@rm -rf backend/.venv
	@rm -rf frontend/node_modules
	@rm -rf frontend/.next
	@rm -rf frontend/out
