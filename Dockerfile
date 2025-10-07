# Usa la imagen oficial de NVIDIA con CUDA 12.1.1 y herramientas de desarrollo
FROM nvidia/cuda:12.1.1-devel-ubuntu22.04

# Evita que la instalación pida interacción del usuario
ENV DEBIAN_FRONTEND=noninteractive

# Instala Python 3, pip y git
RUN apt-get update && \
    apt-get install -y python3 python3-pip git && \
    rm -rf /var/lib/apt/lists/*

# Establece el directorio de trabajo
WORKDIR /app

# Copia tu código de handler al contenedor
COPY ./rp_handler.py /app/rp_handler.py

# Instala las dependencias de Python
# Se instala PyTorch primero, especificando la versión compatible con CUDA 12.1
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121 && \
    pip install --no-cache-dir runpod diffusers transformers accelerate sentencepiece Pillow

# Comando que se ejecuta al iniciar el contenedor
CMD ["python3", "-u", "/app/rp_handler.py"]
