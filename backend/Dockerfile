FROM python:3.10-slim

ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y \
    ffmpeg pkg-config build-essential \
    libavformat-dev libavcodec-dev libavdevice-dev \
    libavutil-dev libswscale-dev libswresample-dev libavfilter-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu

WORKDIR /app
COPY . /app

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]