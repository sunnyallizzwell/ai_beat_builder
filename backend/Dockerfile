FROM python:3.10-slim

ENV PYTHONUNBUFFERED=1

# Install OS-level dependencies, C-compilers, and FFmpeg dev headers for PyAV/Audiocraft
RUN apt-get update && apt-get install -y \
    procps \
    ffmpeg \
    pkg-config \
    build-essential \
    libavformat-dev \
    libavcodec-dev \
    libavdevice-dev \
    libavutil-dev \
    libswscale-dev \
    libswresample-dev \
    libavfilter-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Upgrade pip first, then install requirements
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Force CPU-only PyTorch to save massive amounts of disk space
RUN pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu

# Install headless browser for scraping
RUN playwright install chromium --with-deps

WORKDIR /app
COPY . /app

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]