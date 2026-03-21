FROM python:3.10-slim

ENV PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

WORKDIR /app
COPY . /app

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8050", "app:server"]