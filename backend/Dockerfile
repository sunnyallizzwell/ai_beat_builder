FROM python:3.10-slim

ENV PYTHONUNBUFFERED=1

# 1. Install ONLY the basic FFmpeg runtime
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 2. Update pip and core tools
RUN pip install --upgrade pip setuptools wheel

# 3. Install CPU-only PyTorch first
RUN pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu

# 4. THE VERSION LOCK: 
# - "numpy<2.0.0" stops the Numpy 2.0 C++ math crash.
# - "transformers<4.41.0" stops HuggingFace from rejecting Audiocraft's PyTorch 2.1.0 requirement.
# - --only-binary=av bypasses the PyAV compiler loop.
RUN pip install --no-cache-dir "numpy<2.0.0" "transformers<4.41.0" fastapi uvicorn pretty_midi scipy audiocraft --only-binary=av

COPY . /app

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]