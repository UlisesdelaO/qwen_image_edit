#!/bin/bash

# Script de despliegue automatizado para RunPod
# Uso: ./deploy_runpod.sh [docker_username]

set -e  # Salir si hay algún error

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para logging
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Verificar argumentos
if [ $# -eq 0 ]; then
    error "Uso: $0 <docker_username>"
    echo "Ejemplo: $0 tuusuario"
    exit 1
fi

DOCKER_USERNAME=$1
IMAGE_NAME="qwen-image-edit"
IMAGE_TAG="latest"
FULL_IMAGE_NAME="${DOCKER_USERNAME}/${IMAGE_NAME}:${IMAGE_TAG}"

log "=== INICIANDO DESPLIEGUE EN RUNPOD ==="
log "Docker Username: $DOCKER_USERNAME"
log "Image Name: $FULL_IMAGE_NAME"

# Verificar que Docker está corriendo
log "Verificando Docker..."
if ! docker info > /dev/null 2>&1; then
    error "Docker no está corriendo. Por favor inicia Docker Desktop."
    exit 1
fi
success "Docker está funcionando"

# Verificar que estás logueado en Docker Hub
log "Verificando login en Docker Hub..."
if ! docker info | grep -q "Username: $DOCKER_USERNAME"; then
    warning "No estás logueado en Docker Hub como $DOCKER_USERNAME"
    log "Ejecutando: docker login"
    docker login
fi
success "Login en Docker Hub verificado"

# Construir la imagen
log "Construyendo imagen Docker..."
log "Esto puede tardar varios minutos..."

if docker build -t "$FULL_IMAGE_NAME" .; then
    success "Imagen construida exitosamente"
else
    error "Error construyendo la imagen"
    exit 1
fi

# Mostrar información de la imagen
log "Información de la imagen:"
docker images "$FULL_IMAGE_NAME"

# Subir la imagen a Docker Hub
log "Subiendo imagen a Docker Hub..."
if docker push "$FULL_IMAGE_NAME"; then
    success "Imagen subida exitosamente a Docker Hub"
else
    error "Error subiendo la imagen"
    exit 1
fi

# Crear archivo de configuración para RunPod
log "Creando archivo de configuración para RunPod..."
cat > runpod_config.json << EOF
{
  "name": "Qwen-Image-Edit",
  "description": "Qwen-Image-Edit (20B MMDiT) para edición de imágenes con logging detallado",
  "image": "$FULL_IMAGE_NAME",
  "gpu_types": ["RTX 4090", "A100"],
  "min_memory": 24,
  "min_vcpu": 8,
  "min_disk": 50,
  "timeout": 300,
  "idle_timeout": 60,
  "max_workers": 1,
  "environment_variables": {
    "CUDA_VISIBLE_DEVICES": "0",
    "PYTHONUNBUFFERED": "1",
    "HF_HOME": "/app/cache",
    "TRANSFORMERS_CACHE": "/app/cache"
  },
  "docker_args": "--gpus all"
}
EOF

success "Archivo de configuración creado: runpod_config.json"

# Mostrar instrucciones para RunPod
log "=== INSTRUCCIONES PARA RUNPOD ==="
echo ""
echo "1. Ve a https://console.runpod.io/"
echo "2. Selecciona 'Serverless'"
echo "3. Crea un nuevo Template con estos datos:"
echo "   - Container Image: $FULL_IMAGE_NAME"
echo "   - GPU Type: RTX 4090 (24GB) o A100 (40GB)"
echo "   - Memory: 32GB+"
echo "   - Storage: 50GB+"
echo "   - Timeout: 300 segundos"
echo "   - Max Workers: 1"
echo ""
echo "4. Variables de entorno:"
echo "   - CUDA_VISIBLE_DEVICES=0"
echo "   - PYTHONUNBUFFERED=1"
echo "   - HF_HOME=/app/cache"
echo "   - TRANSFORMERS_CACHE=/app/cache"
echo ""
echo "5. Despliega el template"
echo "6. Prueba con el endpoint generado"
echo ""

# Crear script de prueba
log "Creando script de prueba..."
cat > test_runpod_api.py << 'EOF'
#!/usr/bin/env python3
"""
Script de prueba para la API de RunPod
"""

import requests
import base64
import json
from PIL import Image
from io import BytesIO

def create_test_image():
    """Crear una imagen de prueba"""
    img = Image.new('RGB', (512, 512), color='lightblue')
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")

def test_runpod_api(endpoint_url, api_key):
    """Probar la API de RunPod"""
    
    print("=== PROBANDO API DE RUNPOD ===")
    
    # Crear imagen de prueba
    test_image = create_test_image()
    
    # Datos de la petición
    payload = {
        "input": {
            "prompt": "A beautiful mountain landscape with a lake",
            "user_image": test_image
        }
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    print(f"Enviando petición a: {endpoint_url}")
    print(f"Prompt: {payload['input']['prompt']}")
    print(f"Tamaño de imagen: {len(test_image)} caracteres")
    
    try:
        response = requests.post(endpoint_url, json=payload, headers=headers, timeout=300)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if "image_base64" in result:
                print("✅ ¡Éxito! Imagen generada correctamente")
                
                # Guardar imagen resultante
                img_data = base64.b64decode(result["image_base64"])
                with open("runpod_test_result.png", "wb") as f:
                    f.write(img_data)
                print("💾 Imagen guardada como 'runpod_test_result.png'")
                
                return True
            else:
                print("❌ Error en la respuesta:", result)
                return False
        else:
            print(f"❌ Error HTTP {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error durante la petición: {str(e)}")
        return False

if __name__ == "__main__":
    # Reemplaza estos valores con los de tu endpoint
    ENDPOINT_URL = "https://YOUR_ENDPOINT_ID.api.runpod.ai/runsync"
    API_KEY = "YOUR_API_KEY"
    
    print("⚠️  IMPORTANTE: Actualiza ENDPOINT_URL y API_KEY en el script")
    print("   antes de ejecutar la prueba")
    print("")
    
    # Descomenta la siguiente línea cuando tengas los valores correctos
    # test_runpod_api(ENDPOINT_URL, API_KEY)
EOF

chmod +x test_runpod_api.py
success "Script de prueba creado: test_runpod_api.py"

# Mostrar resumen final
log "=== DESPLIEGUE COMPLETADO ==="
echo ""
echo "✅ Imagen Docker: $FULL_IMAGE_NAME"
echo "✅ Configuración: runpod_config.json"
echo "✅ Script de prueba: test_runpod_api.py"
echo ""
echo "📋 Próximos pasos:"
echo "1. Configura el template en RunPod"
echo "2. Obtén el endpoint URL y API key"
echo "3. Actualiza test_runpod_api.py con tus credenciales"
echo "4. Ejecuta: python3 test_runpod_api.py"
echo ""
echo "🔍 Para monitorear logs:"
echo "   - Ve a la consola de RunPod"
echo "   - Selecciona tu endpoint"
echo "   - Ve a la pestaña 'Logs'"
echo ""
success "¡Despliegue completado exitosamente!"
