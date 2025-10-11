# Qwen Image Edit - RunPod Serverless

Este proyecto implementa un handler de RunPod Serverless para edición de imágenes usando el modelo Qwen-Image-Edit.

## 🚀 Despliegue Automático con GitHub Actions

### Configuración de Secrets

Para que el despliegue automático funcione, necesitas configurar estos secrets en tu repositorio de GitHub:

1. Ve a tu repositorio en GitHub
2. Click en **Settings** → **Secrets and variables** → **Actions**
3. Agrega estos secrets:

#### `DOCKER_USERNAME`
- Tu nombre de usuario de Docker Hub
- Ejemplo: `tuusuario`

#### `DOCKER_PASSWORD`
- Tu token de acceso de Docker Hub (no tu contraseña)
- Ve a Docker Hub → Account Settings → Security → New Access Token

### Flujo de Despliegue

1. **Push automático**: Cada vez que hagas `git push` a la rama `main`, GitHub Actions:
   - Construirá automáticamente la imagen Docker
   - La subirá a Docker Hub
   - Te notificará que está lista

2. **Actualizar RunPod**: Después del push exitoso:
   - Ve a tu template en RunPod
   - Actualiza la imagen Docker con: `tuusuario/qwen-image-edit:latest`
   - Guarda los cambios

### Despliegue Manual

Si prefieres hacer el despliegue manualmente:

```bash
# 1. Instalar Docker Desktop
# 2. Construir la imagen
docker build -t tuusuario/qwen-image-edit:latest .

# 3. Subir a Docker Hub
docker push tuusuario/qwen-image-edit:latest

# 4. Actualizar template en RunPod
```

## 📋 Características

- ✅ Logging completo de cada paso
- ✅ Manejo de errores con traceback
- ✅ Medición de tiempos de ejecución
- ✅ Soporte para imágenes base64
- ✅ Máscaras opcionales
- ✅ Optimizado para CUDA

## 🔧 Uso

El handler espera estos parámetros:

```json
{
  "prompt": "Descripción de la edición",
  "user_image": "imagen_en_base64",
  "mask_image": "mascara_en_base64" // opcional
}
```

Retorna:
```json
{
  "image_base64": "imagen_editada_en_base64"
}
```
