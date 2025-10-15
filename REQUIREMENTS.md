# Requerimientos para Qwen-Image-Edit en RunPod

## 🖥️ **Requerimientos de Hardware**

### **Configuración Mínima Recomendada:**
- **GPU**: NVIDIA RTX 4090 (24GB VRAM) o superior
- **RAM**: 32GB+
- **Storage**: 50GB+ SSD
- **CUDA**: 12.1+

### **Configuración Óptima:**
- **GPU**: NVIDIA A100 (40GB VRAM) o H100 (80GB VRAM)
- **RAM**: 64GB+
- **Storage**: 100GB+ NVMe SSD
- **CUDA**: 12.1+

## 🔧 **Requerimientos de Software**

### **Sistema Operativo:**
- Ubuntu 22.04 LTS (recomendado)
- CUDA 12.1+
- Python 3.8+

### **Dependencias Python:**
```bash
torch>=2.0.0
torchvision>=0.15.0
torchaudio>=2.0.0
diffusers>=0.21.0
transformers>=4.35.0
accelerate>=0.20.0
sentencepiece>=0.1.99
Pillow>=9.0.0
runpod>=1.0.0
safetensors>=0.3.0
xformers>=0.0.20  # Opcional, para optimización
```

## ⚙️ **Configuración de RunPod**

### **Template Settings:**
- **Container Image**: `tuusuario/qwen-image-edit:latest`
- **GPU Type**: RTX 4090 (24GB) o A100 (40GB)
- **Memory**: 32GB+ RAM
- **Storage**: 50GB+ SSD
- **Timeout**: 300 segundos
- **Max Workers**: 1 (debido al tamaño del modelo)

### **Variables de Entorno:**
```bash
CUDA_VISIBLE_DEVICES=0
PYTHONUNBUFFERED=1
HF_HOME=/app/cache
TRANSFORMERS_CACHE=/app/cache
```

## 📊 **Especificaciones del Modelo**

### **Qwen-Image-Edit (20B MMDiT):**
- **Parámetros**: 20 mil millones
- **Arquitectura**: MMDiT (Multi-Modal Diffusion Transformer)
- **Capacidades**:
  - Edición precisa de imágenes
  - Renderizado de texto complejo (especialmente chino)
  - Soporte multi-imagen (1-3 imágenes)
  - ControlNet nativo
  - Preservación de identidad facial
  - Edición de productos con consistencia

### **Uso de Memoria:**
- **VRAM**: ~18-20GB para inferencia
- **RAM**: ~8-10GB adicionales
- **Storage**: ~40GB para el modelo completo

## 🚀 **Optimizaciones Recomendadas**

### **Para RunPod Serverless:**
1. **Memory Efficient Attention**: Habilitado por defecto
2. **Model CPU Offload**: Para reducir uso de VRAM
3. **Float16 Precision**: Para optimizar memoria
4. **XFormers**: Para aceleración (opcional)

### **Configuración de Pipeline:**
```python
pipeline = QwenImageEditPipeline.from_pretrained(
    "Qwen/Qwen-Image-Edit",
    torch_dtype=torch.float16,
    low_cpu_mem_usage=True,
    use_safetensors=True
).to("cuda")

# Optimizaciones
pipeline.enable_memory_efficient_attention()
pipeline.enable_model_cpu_offload()
```

## 💰 **Estimación de Costos RunPod**

### **RTX 4090 (24GB):**
- **Cold Start**: ~2-3 minutos
- **Costo por minuto**: ~$0.50-0.80
- **Costo por request**: ~$1.50-2.40

### **A100 (40GB):**
- **Cold Start**: ~1-2 minutos
- **Costo por minuto**: ~$1.00-1.50
- **Costo por request**: ~$2.00-3.00

## 🔍 **Monitoreo y Debugging**

### **Logs Importantes:**
- Tiempo de carga del modelo
- Uso de memoria VRAM/RAM
- Tiempo de inferencia por request
- Errores de CUDA/memoria

### **Métricas a Monitorear:**
- Latencia de respuesta
- Throughput (requests/minuto)
- Uso de recursos
- Tasa de errores

## 📝 **Notas Importantes**

1. **Primera Carga**: El modelo puede tardar 2-3 minutos en cargar inicialmente
2. **Memoria**: El modelo requiere al menos 20GB de VRAM
3. **Concurrencia**: Recomendado 1 worker por instancia debido al tamaño
4. **Cache**: El modelo se cachea en `/app/cache` para cargas posteriores
5. **Timeout**: Configurar timeout de al menos 300 segundos para requests complejos
