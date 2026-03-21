FROM python:3.10-slim

ENV PYTHONUNBUFFERED=1

# 1. Install ONLY the basic FFmpeg runtime. Zero C++ dev headers needed.
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 2. Update pip and core tools
RUN pip install --upgrade pip setuptools wheel

# 3. Install CPU-only PyTorch first
RUN pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu

# 4. THE ULTIMATE FIX: Install everything in one single command.
# By attaching --only-binary=av to the same line as audiocraft, we globally block pip 
# from compiling ANY version of PyAV from source, forcing it to use the pre-compiled wheel.
RUN pip install --no-cache-dir fastapi uvicorn pretty_midi scipy audiocraft --only-binary=av

COPY . /app

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]