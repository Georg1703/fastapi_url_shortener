FROM python:3.12-slim

WORKDIR /code
RUN pip install poetry
COPY ./pyproject.toml ./poetry.lock /
RUN poetry export -f requirements.txt --output /code/requirements.txt --without-hashes

RUN apt-get update && apt-get install -y \ 
    gcc python3-dev libpq-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

COPY . /code

RUN python3 -m pip install --no-cache-dir --upgrade -r requirements.txt

EXPOSE 80

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "80", "--reload"]