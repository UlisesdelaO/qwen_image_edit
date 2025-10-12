# CRITICAL FIX: October 12, 2025 - Fixed QwenImageEditPipeline import error
# This version uses StableDiffusionInpaintPipeline instead of QwenImageEditPipeline
FROM nvidia/cuda:12.1.1-devel-ubuntu22.04

# Evita que la instalación pida interacción del usuario
ENV DEBIAN_FRONTEND=noninteractive

# Configurar variables de entorno para optimización
ENV PYTHONUNBUFFERED=1
ENV CUDA_VISIBLE_DEVICES=0

# Instala Python 3, pip y git
RUN apt-get update && \
    apt-get install -y python3 python3-pip git && \
    rm -rf /var/lib/apt/lists/*

# Establece el directorio de trabajo
WORKDIR /app

# Copia tu código de handler al contenedor
COPY ./rp_handler.py /app/rp_handler.py

# Instala las dependencias de Python paso a paso para evitar errores
RUN pip install --no-cache-dir --upgrade pip

# Instala PyTorch con CUDA 12.1
RUN pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Instala dependencias básicas
RUN pip install --no-cache-dir runpod diffusers transformers accelerate sentencepiece Pillow

# Intenta instalar xformers (opcional, puede fallar)
RUN pip install --no-cache-dir xformers || echo "xformers installation failed, continuing without it"

# Limpia cache
RUN pip cache purge

# Comando que se ejecuta al iniciar el contenedor
CMD ["python3", "-u", "/app/rp_handler.py"]
