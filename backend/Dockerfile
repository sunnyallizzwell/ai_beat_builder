FROM python:3.10-slim

ENV PYTHONUNBUFFERED=1

# 1. Install system compilers, FFmpeg, and Python dev headers
RUN apt-get update && apt-get install -y \
    ffmpeg \
    pkg-config \
    build-essential \
    python3-dev \
    libavformat-dev libavcodec-dev libavdevice-dev \
    libavutil-dev libswscale-dev libswresample-dev libavfilter-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# 2. Upgrade core build tools
RUN pip install --upgrade pip setuptools wheel cython

# 3. CRITICAL: Install CPU-only PyTorch FIRST so Audiocraft doesn't download the 4GB GPU version
RUN pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu

# 4. CRITICAL: Force Pip to use a pre-compiled binary for PyAV so it skips the C++ build
RUN pip install av --only-binary=av

# 5. Install the remaining requirements (Audiocraft, FastAPI, etc.)
RUN pip install --no-cache-dir -r requirements.txt

WORKDIR /app
COPY . /app

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]