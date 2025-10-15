#!/bin/bash

# Script para construir y ejecutar Qwen-Image-Edit localmente
# Uso: ./build_local.sh

echo "=== CONSTRUYENDO QWEN-IMAGE-EDIT LOCAL ==="

# Verificar que Docker está corriendo
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker no está corriendo. Por favor inicia Docker Desktop."
    exit 1
fi

# Verificar que NVIDIA Docker está disponible
if ! docker run --rm --gpus all nvidia/cuda:12.1.1-base-ubuntu22.04 nvidia-smi > /dev/null 2>&1; then
    echo "❌ NVIDIA Docker no está configurado correctamente."
    echo "Instala nvidia-docker2: https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html"
    exit 1
fi

echo "✅ Docker y NVIDIA Docker están funcionando"

# Construir la imagen local
echo "🔨 Construyendo imagen local..."
docker build -f Dockerfile.local -t qwen-image-edit-local .

if [ $? -eq 0 ]; then
    echo "✅ Imagen construida exitosamente"
else
    echo "❌ Error construyendo la imagen"
    exit 1
fi

# Crear directorio para cache si no existe
mkdir -p ./cache

echo "🚀 Iniciando contenedor local..."
echo "📝 Jupyter Lab estará disponible en: http://localhost:8888"
echo "🛑 Para detener: Ctrl+C"

# Ejecutar el contenedor
docker run --rm -it \
    --gpus all \
    -p 8888:8888 \
    -v $(pwd)/cache:/app/cache \
    -v $(pwd):/app/workspace \
    qwen-image-edit-local
