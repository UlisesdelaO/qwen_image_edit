# 📊 Guía de Monitoreo de Logs - Qwen-Image-Edit RunPod

Esta guía te ayuda a monitorear y diagnosticar el funcionamiento de tu API en RunPod.

## 🔍 **Tipos de Logs Disponibles**

### **1. Logs de Inicio (Startup)**
```
=== QWEN-IMAGE-EDIT RUNPOD STARTUP ===
Timestamp: 2025-10-15 10:30:00
CUDA Version: release 12.1
Python Version: Python 3.8.10
PyTorch Version: 2.0.1+cu121
GPU Info: RTX 4090, 24576
Starting handler...
```

### **2. Logs de Carga del Modelo**
```
=== INICIANDO CARGA DEL MODELO ===
=== INFORMACIÓN DEL SISTEMA ===
PyTorch version: 2.0.1+cu121
CUDA disponible: True
CUDA version: 12.1
GPU: NVIDIA GeForce RTX 4090
VRAM total: 24.0 GB
VRAM libre: 24.0 GB
```

### **3. Logs de Procesamiento de Requests**
```
=== INICIANDO PROCESAMIENTO DE TRABAJO [req_1697362200000] ===
Job ID: job_12345
Request ID: req_1697362200000
Timestamp: 2025-10-15 10:35:00
```

### **4. Logs de Métricas**
```
METRICS: req_1697362200000 | Total: 45.2s | Pipeline: 42.1s | Success: True
```

## 📈 **Métricas Importantes a Monitorear**

### **Tiempos de Respuesta**
- **Carga del modelo**: 2-5 minutos (solo en cold start)
- **Procesamiento por request**: 30-60 segundos
- **Tiempo total**: 35-65 segundos

### **Uso de Memoria**
- **VRAM total**: 24GB (RTX 4090)
- **VRAM usada**: 18-22GB
- **VRAM libre**: 2-6GB

### **Tasas de Éxito**
- **Requests exitosos**: >95%
- **Errores de memoria**: <1%
- **Timeouts**: <2%

## 🚨 **Señales de Alerta**

### **⚠️ Advertencias**
```
WARNING: Pipeline no inicializado, ejecutando init()...
WARNING: VRAM libre restante: 1.2 GB
```

### **❌ Errores Críticos**
```
ERROR: CUDA Out of Memory
ERROR: No se pudo cargar el modelo
ERROR: Pipeline no inicializado
```

### **🔴 Fallos del Sistema**
```
=== FALLO EN CARGA DEL MODELO ===
=== PROCESAMIENTO DE TRABAJO FALLÓ ===
```

## 🔧 **Cómo Monitorear en RunPod**

### **1. Acceder a los Logs**
1. Ve a https://console.runpod.io/
2. Selecciona "Serverless"
3. Encuentra tu endpoint
4. Haz clic en "Logs"

### **2. Filtrar Logs**
- **Por nivel**: INFO, WARNING, ERROR
- **Por componente**: runpod, metrics
- **Por request**: req_1697362200000

### **3. Buscar Patrones**
```bash
# Buscar errores
grep "ERROR" logs.txt

# Buscar métricas
grep "METRICS" logs.txt

# Buscar requests específicos
grep "req_1697362200000" logs.txt
```

## 📊 **Dashboard de Monitoreo**

### **Métricas en Tiempo Real**
- **Requests/minuto**: 0.5-2.0
- **Tiempo promedio**: 45 segundos
- **Tasa de éxito**: 95%+
- **Uso de VRAM**: 85-95%

### **Alertas Automáticas**
- **VRAM > 95%**: Reducir tamaño de imagen
- **Tiempo > 60s**: Verificar GPU
- **Errores > 5%**: Revisar logs

## 🛠️ **Solución de Problemas**

### **Problema: Modelo no carga**
```
ERROR: No se pudo cargar el modelo
```
**Solución:**
- Verificar VRAM disponible (mínimo 20GB)
- Revisar conexión a Hugging Face
- Reiniciar el endpoint

### **Problema: CUDA Out of Memory**
```
ERROR: CUDA Out of Memory
```
**Solución:**
- Reducir tamaño de imagen (512x512 → 256x256)
- Reducir inference steps (20 → 10)
- Usar GPU con más VRAM

### **Problema: Timeout**
```
ERROR: Request timeout
```
**Solución:**
- Aumentar timeout en RunPod (300s → 600s)
- Optimizar prompt (más corto)
- Verificar carga del modelo

### **Problema: Imagen corrupta**
```
ERROR: No se generó ninguna imagen
```
**Solución:**
- Verificar formato de imagen base64
- Revisar prompt (evitar caracteres especiales)
- Comprobar máscara si se usa

## 📝 **Logs de Ejemplo**

### **✅ Request Exitoso**
```
2025-10-15 10:35:00 - __main__ - INFO - [rp_handler.py:127] - === INICIANDO PROCESAMIENTO DE TRABAJO [req_1697362200000] ===
2025-10-15 10:35:00 - __main__ - INFO - [rp_handler.py:134] - Job ID: job_12345
2025-10-15 10:35:00 - __main__ - INFO - [rp_handler.py:135] - Request ID: req_1697362200000
2025-10-15 10:35:00 - __main__ - INFO - [rp_handler.py:136] - Timestamp: 2025-10-15 10:35:00
2025-10-15 10:35:00 - __main__ - INFO - [rp_handler.py:144] - Pipeline ya está inicializado, continuando...
2025-10-15 10:35:00 - __main__ - INFO - [rp_handler.py:147] - === VALIDACIÓN DE ENTRADA ===
2025-10-15 10:35:00 - __main__ - INFO - [rp_handler.py:154] - Entrada validada exitosamente
2025-10-15 10:35:00 - __main__ - INFO - [rp_handler.py:156] - Prompt recibido: A beautiful mountain landscape with a lake...
2025-10-15 10:35:00 - __main__ - INFO - [rp_handler.py:157] - Tamaño de imagen del usuario: 123456 caracteres en base64
2025-10-15 10:35:00 - __main__ - INFO - [rp_handler.py:159] - === PROCESAMIENTO DE IMÁGENES ===
2025-10-15 10:35:00 - __main__ - INFO - [rp_handler.py:164] - Imagen del usuario decodificada: (512, 512) (RGB)
2025-10-15 10:35:00 - __main__ - INFO - [rp_handler.py:176] - === EJECUCIÓN DEL PIPELINE ===
2025-10-15 10:35:00 - __main__ - INFO - [rp_handler.py:185] - VRAM antes de inferencia: 18.5 GB
2025-10-15 10:35:42 - __main__ - INFO - [rp_handler.py:199] - Pipeline ejecutado exitosamente en 42.1 segundos
2025-10-15 10:35:42 - __main__ - INFO - [rp_handler.py:200] - Imagen resultante: (512, 512) (RGB)
2025-10-15 10:35:42 - __main__ - INFO - [rp_handler.py:203] - VRAM después de inferencia: 19.2 GB
2025-10-15 10:35:42 - __main__ - INFO - [rp_handler.py:206] - === CONVERSIÓN DE RESULTADO ===
2025-10-15 10:35:42 - __main__ - INFO - [rp_handler.py:212] - Imagen convertida a base64: 234567 caracteres
2025-10-15 10:35:42 - __main__ - INFO - [rp_handler.py:215] - === PROCESAMIENTO COMPLETADO ===
2025-10-15 10:35:42 - __main__ - INFO - [rp_handler.py:216] - Tiempo total: 45.2 segundos
2025-10-15 10:35:42 - __main__ - INFO - [rp_handler.py:217] - Tiempo de pipeline: 42.1 segundos
2025-10-15 10:35:42 - __main__ - INFO - [rp_handler.py:218] - Tiempo de procesamiento: 3.1 segundos
2025-10-15 10:35:42 - __main__ - INFO - [rp_handler.py:219] - Request ID: req_1697362200000
2025-10-15 10:35:42 - __main__ - INFO - [rp_handler.py:220] - === PROCESAMIENTO DE TRABAJO COMPLETADO EXITOSAMENTE ===
2025-10-15 10:35:42 - metrics - INFO - [rp_handler.py:223] - METRICS: req_1697362200000 | Total: 45.2s | Pipeline: 42.1s | Success: True
```

### **❌ Request con Error**
```
2025-10-15 10:40:00 - __main__ - ERROR - [rp_handler.py:230] - === ERROR DURANTE EL PROCESAMIENTO ===
2025-10-15 10:40:00 - __main__ - ERROR - [rp_handler.py:231] - Request ID: req_1697362200001
2025-10-15 10:40:00 - __main__ - ERROR - [rp_handler.py:232] - Tiempo transcurrido antes del error: 2.5 segundos
2025-10-15 10:40:00 - __main__ - ERROR - [rp_handler.py:233] - Error: CUDA out of memory
2025-10-15 10:40:00 - __main__ - ERROR - [rp_handler.py:234] - Tipo de error: RuntimeError
2025-10-15 10:40:00 - __main__ - ERROR - [rp_handler.py:238] - VRAM en el momento del error: 23.8 GB
2025-10-15 10:40:00 - metrics - ERROR - [rp_handler.py:242] - METRICS: req_1697362200001 | Total: 2.5s | Success: False | Error: RuntimeError
```

## 🎯 **Mejores Prácticas**

### **1. Monitoreo Continuo**
- Revisar logs diariamente
- Configurar alertas automáticas
- Mantener métricas históricas

### **2. Optimización Basada en Logs**
- Identificar patrones de error
- Ajustar parámetros según métricas
- Escalar recursos cuando sea necesario

### **3. Mantenimiento Preventivo**
- Limpiar logs antiguos
- Monitorear uso de VRAM
- Actualizar dependencias regularmente

---

**¡Con estos logs detallados podrás monitorear y optimizar tu API de Qwen-Image-Edit en RunPod!** 🚀
