FROM python:3.10-slim

ENV PYTHONUNBUFFERED=1

# 1. Install ONLY the basic FFmpeg runtime and wget. Zero C++ dev headers.
RUN apt-get update && apt-get install -y ffmpeg wget && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 2. Update pip and core tools
RUN pip install --upgrade pip setuptools wheel

# 3. Install CPU-only PyTorch first
RUN pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu

# 4. THE SILVER BULLET: Install the pre-compiled binary wheel for PyAV 11.0.0 directly from PyPI's servers.
# This physically stops pip from downloading the tar.gz source and triggering the C++ compiler.
RUN pip install https://files.pythonhosted.org/packages/15/dd/786db90e2d31215bb4b06b72a6b28cc42735160cb81c3c97eeb4c1cde8ba/av-11.0.0-cp310-cp310-manylinux_2_17_x86_64.manylinux2014_x86_64.whl

# 5. Copy requirements and install the rest. Pip will see 'av' is already installed and completely skip it.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]