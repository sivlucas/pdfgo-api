.PHONY: install dev test lint clean run docker-build docker-up docker-down

# Instalação
install:
	pip install -r requirements/base.txt

dev:
	pip install -r requirements/dev.txt
	pre-commit install

# Testes
test:
	pytest tests/ -v --cov=app --cov-report=html

test-watch:
	pytest tests/ -v --cov=app --cov-report=html -f

# Qualidade de código
lint:
	black app/ tests/
	flake8 app/ tests/
	mypy app/

format:
	black app/ tests/
	isort app/ tests/

# Limpeza
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf storage/uploads/* storage/outputs/* storage/temp/*
	rm -rf .coverage htmlcov/ .pytest_cache/

clean-all: clean
	rm -rf build/ dist/ *.egg-info/

# Execução
run:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

run-prod:
	uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

# Docker
docker-build:
	docker-compose build

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

docker-clean:
	docker-compose down -v
	docker system prune -f

# Deploy
deploy: test lint docker-build docker-up

# Desenvolvimento
dev-setup: install dev
	@echo "✅ Ambiente de desenvolvimento configurado!"

.PHONY: help
help:
	@echo "Comandos disponíveis:"
	@echo "  install      - Instala dependências básicas"
	@echo "  dev          - Instala dependências de desenvolvimento"
	@echo "  test         - Executa testes"
	@echo "  lint         - Verifica qualidade do código"
	@echo "  format       - Formata o código"
	@echo "  clean        - Limpa arquivos temporários"
	@echo "  run          - Executa servidor de desenvolvimento"
	@echo "  docker-build - Constrói imagens Docker"
	@echo "  docker-up    - Inicia containers"
	@echo "  docker-down  - Para containers"
	@echo "  deploy       - Deploy completo"
	@echo "  dev-setup    - Configura ambiente de desenvolvimento"