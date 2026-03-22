FROM python:3.10-slim

ENV PYTHONUNBUFFERED=1

# 1. Install ONLY the basic FFmpeg runtime
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN pip install --upgrade pip setuptools wheel

# 2. Install the exact CPU PyTorch version that Audiocraft's backend demands
RUN pip install torch==2.1.0 torchaudio==2.1.0 --index-url https://download.pytorch.org/whl/cpu

# 3. THE QUARANTINE ZONE: 
# Lock NumPy to the 1.x era, and lock Transformers to a version from late 2023.
# This makes them perfectly compatible with PyTorch 2.1.0.
RUN pip install "numpy<2.0.0" "transformers==4.35.2"

# 4. Install Audiocraft and the web framework. 
# Pip will see the quarantined packages and respect the locks.
RUN pip install --no-cache-dir fastapi uvicorn pretty_midi scipy audiocraft --only-binary=av

COPY . /app

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]