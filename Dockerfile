# Dockerfile
FROM runpod/pytorch:2.3.0-py3.10-cuda12.1.1-devel

# Establece el directorio de trabajo
WORKDIR /app

# Instala las dependencias de Python
RUN pip install --upgrade pip && \
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121 && \
    pip install runpod diffusers transformers accelerate sentencepiece

# Copia el código de tu handler al contenedor
COPY ./rp_handler.py /app/rp_handler.py

# Comando que se ejecuta al iniciar el contenedor
CMD ["python", "-u", "/app/rp_handler.py"]
