FROM python:3.14.0b3-slim-bookworm

WORKDIR /app

RUN apt-get update \
  && apt-get install -y python3-dev libpq-dev gcc \
  && rm -rf /var/lib/apt/lists/*

COPY init/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY init/main.py ./main.py
COPY modules ./modules
COPY init/initialize.sql ./initialize.sql
COPY init/docker-entrypoint.sh ./docker-entrypoint.sh
COPY init/data/ ./data

ENV PYTHONUNBUFFERED=1
RUN chmod +x ./docker-entrypoint.sh

ENTRYPOINT ["./docker-entrypoint.sh"]
CMD ["--init"]