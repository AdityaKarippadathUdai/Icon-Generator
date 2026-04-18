# ── Base ──────────────────────────────────────────────────────────────────────
FROM nvidia/cuda:12.1.1-cudnn8-runtime-ubuntu22.04

# ── Environment ───────────────────────────────────────────────────────────────
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# ── System Dependencies ───────────────────────────────────────────────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
        python3 \
        python3-pip \
        python3-dev \
        git \
        libgl1 \
        libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# ── Workdir ───────────────────────────────────────────────────────────────────
WORKDIR /app

# ── Install Dependencies ──────────────────────────────────────────────────────
COPY requirements.txt .

RUN python3 -m pip install --upgrade pip && \
    python3 -m pip install --no-cache-dir \
        torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121 && \
    python3 -m pip install --no-cache-dir -r requirements.txt

# ── Copy ONLY app code ─────────────────────────────────────────────────────────
COPY app/ ./app/

# ❌ DO NOT COPY MODELS HERE

# ── Expose ────────────────────────────────────────────────────────────────────
EXPOSE 8000

# ── Run ───────────────────────────────────────────────────────────────────────
CMD ["python3", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]