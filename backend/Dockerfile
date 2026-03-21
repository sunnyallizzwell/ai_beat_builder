FROM python:3.10-slim

ENV PYTHONUNBUFFERED=1

# 1. Install FFmpeg for audio, and Git to pull the patched repository
RUN apt-get update && apt-get install -y ffmpeg git && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .

# 2. Upgrade pip and build tools
RUN pip install --upgrade pip setuptools wheel

# 3. Install CPU-only PyTorch first
RUN pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu

# 4. THE NUKE: Delete 'audiocraft' from your requirements.txt dynamically
RUN sed -i '/audiocraft/d' requirements.txt

# 5. Install the rest of the normal requirements
RUN pip install --no-cache-dir -r requirements.txt

# 6. Install Meta's patched Audiocraft directly from GitHub. 
# This bypasses the broken PyPI package and seamlessly uses pre-compiled PyAV wheels!
RUN pip install --no-cache-dir git+https://github.com/facebookresearch/audiocraft.git

COPY . /app

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]