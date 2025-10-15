# 🧪 Guía de Pruebas Locales - Qwen-Image-Edit

Esta guía te permite probar Qwen-Image-Edit localmente sin desplegar en RunPod, ahorrando tiempo y dinero.

## 🚀 **Métodos de Prueba**

### **Método 1: Docker Local (Recomendado)**

#### **Paso 1: Verificar Requisitos**
```bash
# Verificar Docker
docker --version

# Verificar NVIDIA Docker
docker run --rm --gpus all nvidia/cuda:12.1.1-base-ubuntu22.04 nvidia-smi

# Verificar GPU disponible
nvidia-smi
```

#### **Paso 2: Construir y Ejecutar**
```bash
# Construir imagen local
./build_local.sh

# O manualmente:
docker build -f Dockerfile.local -t qwen-image-edit-local .
docker run --rm -it --gpus all -p 8888:8888 -v $(pwd)/cache:/app/cache qwen-image-edit-local
```

#### **Paso 3: Acceder a Jupyter Lab**
- Abre tu navegador en: `http://localhost:8888`
- Abre el notebook: `test_qwen_local.ipynb`
- Ejecuta las celdas paso a paso

### **Método 2: Prueba Rápida (Sin Interfaz)**

```bash
# Ejecutar prueba rápida
docker run --rm --gpus all -v $(pwd):/app/workspace qwen-image-edit-local python /app/workspace/quick_test.py
```

### **Método 3: Instalación Local (Solo si tienes 20GB+ VRAM)**

```bash
# Instalar dependencias
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
pip install diffusers>=0.21.0 transformers>=4.35.0 accelerate Pillow

# Ejecutar prueba
python quick_test.py
```

## 📊 **Requisitos de Hardware**

### **Mínimo Recomendado:**
- **GPU**: RTX 4090 (24GB VRAM) o A100 (40GB VRAM)
- **RAM**: 32GB+
- **Storage**: 50GB+ libre

### **Verificación Rápida:**
```bash
# Verificar VRAM disponible
nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits

# Debe mostrar al menos 20,000 MB (20GB)
```

## 🔧 **Configuración Avanzada**

### **Variables de Entorno:**
```bash
export CUDA_VISIBLE_DEVICES=0
export HF_HOME=./cache
export TRANSFORMERS_CACHE=./cache
```

### **Docker con Configuración Personalizada:**
```bash
docker run --rm -it \
    --gpus all \
    -p 8888:8888 \
    -v $(pwd)/cache:/app/cache \
    -v $(pwd):/app/workspace \
    -e CUDA_VISIBLE_DEVICES=0 \
    -e HF_HOME=/app/cache \
    qwen-image-edit-local
```

## 🎯 **Casos de Prueba**

### **1. Prueba Básica:**
- Imagen simple de 512x512
- Prompt básico
- 10 steps de inferencia

### **2. Prueba de Memoria:**
- Monitorear uso de VRAM
- Verificar estabilidad
- Probar múltiples inferencias

### **3. Prueba de Calidad:**
- Diferentes prompts
- Diferentes tamaños de imagen
- Diferentes configuraciones

## 📝 **Scripts Disponibles**

| Script | Descripción | Uso |
|--------|-------------|-----|
| `build_local.sh` | Construir y ejecutar Docker local | `./build_local.sh` |
| `quick_test.py` | Prueba rápida sin interfaz | `python quick_test.py` |
| `test_qwen_local.ipynb` | Notebook interactivo | Abrir en Jupyter Lab |
| `test_qwen_edit.py` | Prueba completa del handler | `python test_qwen_edit.py` |

## 🐛 **Solución de Problemas**

### **Error: CUDA Out of Memory**
```bash
# Verificar VRAM disponible
nvidia-smi

# Si tienes menos de 20GB, usa CPU (más lento)
export CUDA_VISIBLE_DEVICES=""
```

### **Error: Docker no encuentra GPU**
```bash
# Instalar nvidia-docker2
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list
sudo apt-get update && sudo apt-get install -y nvidia-docker2
sudo systemctl restart docker
```

### **Error: Modelo no carga**
```bash
# Limpiar cache
rm -rf ./cache/*

# Verificar conexión a internet
ping huggingface.co
```

## 💡 **Consejos de Optimización**

### **Para Desarrollo:**
- Usa menos steps de inferencia (10-20)
- Imágenes más pequeñas (512x512)
- Limpia memoria entre pruebas

### **Para Producción:**
- Usa más steps (50-100)
- Imágenes más grandes (1024x1024)
- Configuración optimizada de memoria

## 📈 **Monitoreo de Rendimiento**

### **Métricas Importantes:**
- Tiempo de carga del modelo
- Tiempo de inferencia por imagen
- Uso de VRAM/RAM
- Calidad de las imágenes generadas

### **Comandos de Monitoreo:**
```bash
# Monitorear GPU en tiempo real
watch -n 1 nvidia-smi

# Monitorear memoria del sistema
htop
```

## 🎉 **Próximos Pasos**

Una vez que las pruebas locales funcionen correctamente:

1. **Optimizar configuración** basada en los resultados
2. **Ajustar parámetros** del modelo
3. **Probar diferentes prompts** y casos de uso
4. **Desplegar en RunPod** con confianza

---

**¡Disfruta probando Qwen-Image-Edit localmente!** 🚀
