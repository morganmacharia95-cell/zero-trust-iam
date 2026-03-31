FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
COPY packages/ /packages/

RUN pip install --no-cache-dir --no-index --find-links=/packages -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]