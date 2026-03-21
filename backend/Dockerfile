# Switching to 'bullseye' drops the OS back to FFmpeg 4.3, fixing the C++ compiler crash instantly.
FROM python:3.10-bullseye

ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y \
    ffmpeg \
    pkg-config \
    libavformat-dev libavcodec-dev libavdevice-dev \
    libavutil-dev libswscale-dev libswresample-dev libavfilter-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# 1. Upgrade pip and build tools
RUN pip install --upgrade pip setuptools wheel cython

# 2. Force CPU-Only PyTorch first to save massive amounts of RAM
RUN pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu

# 3. Install Audiocraft (Will now compile PyAV flawlessly against FFmpeg 4.3)
RUN pip install --no-cache-dir -r requirements.txt

WORKDIR /app
COPY . /app

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]