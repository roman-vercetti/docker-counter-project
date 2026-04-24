.PHONY: help build up down logs clean shell test

help:
	@echo "🐳 Docker Counter App - Makefile commands:"
	@echo ""
	@echo "  make build   - Build Docker images"
	@echo "  make up      - Start all services (detached)"
	@echo "  make down    - Stop all services"
	@echo "  make logs    - Show logs (follow mode)"
	@echo "  make clean   - Stop and remove volumes"
	@echo "  make shell   - Enter app container"
	@echo "  make test    - Run load test (100 requests)"

build:
	docker compose build

up:
	docker compose up -d
	@echo "✅ App is running at http://localhost:8080"

down:
	docker compose down

logs:
	docker compose logs -f

clean:
	docker compose down -v

shell:
	docker exec -it counter-app /bin/bash

test:
	@echo "🧪 Running load test..."
	@for i in {1..100}; do \
		curl -s http://localhost:8080 > /dev/null; \
		if [ $$((i % 10)) -eq 0 ]; then \
			echo "✅ $$i requests completed"; \
		fi; \
	done
	@echo "✅ Load test completed"
