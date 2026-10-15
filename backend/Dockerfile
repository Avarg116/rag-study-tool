FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir --default-timeout=120 torch --index-url https://download.pytorch.org/whl/cpu

COPY requirements.txt requirements-dev.txt ./
RUN pip install --no-cache-dir --default-timeout=120 -r requirements.txt -r requirements-dev.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
