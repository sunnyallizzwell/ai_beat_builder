FROM python:3.10-slim

ENV PYTHONUNBUFFERED=1

# 1. We only need the base FFmpeg command line tool for audio export, no C++ dev headers
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# 2. Upgrade pip and core tools
RUN pip install --upgrade pip setuptools wheel

# 3. Force CPU-Only PyTorch first
RUN pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu

# 4. THE BYPASS: Force pip to install a pre-compiled binary of PyAV. No compiling allowed.
RUN pip install av --only-binary=av

# 5. Install Audiocraft and the rest. It will see PyAV is already installed and skip the build step entirely.
RUN pip install --no-cache-dir -r requirements.txt

WORKDIR /app
COPY . /app

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]