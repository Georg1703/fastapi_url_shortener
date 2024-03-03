# Short url app

## Prerequisites

1. Docker
2. make (not mandatory)

## Instalation

Once this repository is cloned on your local:

1. Go to fastapi_url_shortener directory.
2. Create .env file with variables that exists in .env_example.
4. Run: `make start` to build and start fastapi uvicorn server + postgres in containers.
5. You are ready to go, open browser and go to http://localhost:8000/docs, you will se 3 available endpoints.
6. Other commands that you can run:
    * `make test` to run available tests
    * `make gen-cov-report-html` to generate html coverage report
    * `make ruff` to check code style