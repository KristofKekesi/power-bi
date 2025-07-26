FROM python:3.14.0b3-slim-bookworm

WORKDIR /app

RUN apt-get update \
 && apt-get install -y python3-dev libpq-dev gcc \
 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .
COPY modules/ ./modules

COPY initialize.sql .
COPY data/ ./data

ENV PYTHONUNBUFFERED=1

ENTRYPOINT ["python", "main.py"]
CMD ["--init"]