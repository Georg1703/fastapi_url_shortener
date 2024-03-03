start:
	docker-compose up --build
build-nocache:
	docker-compose build --no-cache
up:
	docker-compose up
test:
	docker-compose exec fastapi_app pytest
gen-cov-report:
	docker-compose exec fastapi_app pytest --cov=src
gen-cov-report-html:
	docker-compose exec fastapi_app pytest --cov=src --cov-report=html
ruff:
	docker-compose exec fastapi_app ruff check .