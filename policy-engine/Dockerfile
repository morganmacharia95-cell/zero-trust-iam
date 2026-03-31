FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

# Try local packages first (dev), fall back to pip install (CI)
RUN if [ -d "packages" ]; then \
      pip install --no-cache-dir --no-index --find-links=packages -r requirements.txt; \
    else \
      pip install --no-cache-dir -r requirements.txt; \
    fi

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
