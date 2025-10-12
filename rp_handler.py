# rp_handler.py
import runpod
import torch
from diffusers import QwenImageEditPipeline
from runpod.serverless.utils.rp_validator import validate
from PIL import Image
import base64
from io import BytesIO
import logging
import time
import traceback

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('qwen_image_edit.log')
    ]
)
logger = logging.getLogger(__name__)

# Esquema de validación para las entradas de la API
INPUT_SCHEMA = {
    'prompt': {'type': str, 'required': True},
    'user_image': {'type': str, 'required': True}, # Imagen del usuario en base64
    'mask_image': {'type': str, 'required': False} # Máscara opcional en base64
}

# Variable global para mantener el modelo cargado
pipeline = None

def init():
    """
    Esta función se ejecuta una sola vez al iniciar el worker.
    Carga el modelo en la memoria de la GPU.
    """
    logger.info("=== INICIANDO CARGA DEL MODELO ===")
    start_time = time.time()
    
    global pipeline
    
    try:
        logger.info("Limpiando caché de CUDA...")
        torch.cuda.empty_cache()
        logger.info("Caché de CUDA limpiado exitosamente")

        logger.info("Iniciando carga del pipeline Qwen-Image-Edit...")
        logger.info("Modelo: Qwen/Qwen-Image-Edit")
        logger.info("Tipo de datos: torch.float16")
        logger.info("Dispositivo: CUDA")
        
        # Carga el pipeline de Qwen-Image-Edit con optimizaciones
        pipeline = QwenImageEditPipeline.from_pretrained(
            "Qwen/Qwen-Image-Edit",
            torch_dtype=torch.float16,
            low_cpu_mem_usage=True,
            use_safetensors=True
        ).to("cuda")
        
        # Habilitar optimizaciones de memoria
        pipeline.enable_memory_efficient_attention()
        pipeline.enable_model_cpu_offload()

        load_time = time.time() - start_time
        logger.info(f"Pipeline cargado exitosamente en {load_time:.2f} segundos")
        logger.info("Pipeline inicializado y listo para procesar imágenes")
        logger.info("=== CARGA DEL MODELO COMPLETADA ===")
        
        return pipeline
        
    except Exception as e:
        logger.error(f"Error durante la carga del modelo: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise


def handler(job):
    """
    Esta función se ejecuta por cada llamada a la API.
    Procesa la entrada y devuelve la imagen generada.
    """
    logger.info("=== INICIANDO PROCESAMIENTO DE TRABAJO ===")
    start_time = time.time()
    
    try:
        global pipeline
        if pipeline is None:
            logger.info("Pipeline no inicializado, ejecutando init()...")
            pipeline = init()
        else:
            logger.info("Pipeline ya está inicializado, continuando...")

        logger.info("Validando entrada del trabajo...")
        # Valida la entrada del trabajo contra el esquema
        validated_input = validate(job['input'], INPUT_SCHEMA)
        if 'errors' in validated_input:
            logger.error(f"Errores de validación encontrados: {validated_input['errors']}")
            return {"error": validated_input['errors']}
        
        logger.info("Entrada validada exitosamente")
        job_input = validated_input['validated_input']
        
        logger.info(f"Prompt recibido: {job_input['prompt'][:100]}...")
        logger.info(f"Tamaño de imagen del usuario: {len(job_input['user_image'])} caracteres en base64")
        
        logger.info("Decodificando imagen del usuario de base64...")
        # Decodificar la imagen del usuario de base64 a PIL.Image
        user_img_bytes = base64.b64decode(job_input['user_image'])
        user_image = Image.open(BytesIO(user_img_bytes))
        logger.info(f"Imagen del usuario decodificada: {user_image.size} ({user_image.mode})")

        # Decodificar la máscara si se proporciona
        mask_image = None
        if job_input.get('mask_image'):
            logger.info("Máscara proporcionada, decodificando...")
            mask_img_bytes = base64.b64decode(job_input['mask_image'])
            mask_image = Image.open(BytesIO(mask_img_bytes))
            logger.info(f"Máscara decodificada: {mask_image.size} ({mask_image.mode})")
        else:
            logger.info("No se proporcionó máscara, continuando sin ella")

        logger.info("Ejecutando pipeline de edición de imagen...")
        logger.info("Parámetros:")
        logger.info(f"  - Strength: 0.9")
        logger.info(f"  - Guidance scale: 7.5")
        logger.info(f"  - Máscara: {'Sí' if mask_image else 'No'}")
        
        pipeline_start = time.time()
        # Ejecuta el pipeline de edición
        result_image = pipeline(
            prompt=job_input['prompt'],
            image=user_image,
            mask_image=mask_image, # mask_image es opcional
            strength=0.9,
            guidance_scale=7.5
        ).images[0]
        
        pipeline_time = time.time() - pipeline_start
        logger.info(f"Pipeline ejecutado exitosamente en {pipeline_time:.2f} segundos")
        logger.info(f"Imagen resultante: {result_image.size} ({result_image.mode})")

        logger.info("Convirtiendo imagen resultante a base64...")
        # Convierte la imagen de resultado a base64 para devolverla en la respuesta JSON
        buffered = BytesIO()
        result_image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
        logger.info(f"Imagen convertida a base64: {len(img_str)} caracteres")

        total_time = time.time() - start_time
        logger.info(f"Procesamiento completado exitosamente en {total_time:.2f} segundos")
        logger.info("=== PROCESAMIENTO DE TRABAJO COMPLETADO ===")

        # Devuelve la imagen como una cadena base64
        return {"image_base64": img_str}
        
    except Exception as e:
        total_time = time.time() - start_time
        logger.error(f"Error durante el procesamiento del trabajo: {str(e)}")
        logger.error(f"Tiempo transcurrido antes del error: {total_time:.2f} segundos")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return {"error": f"Error interno del servidor: {str(e)}"}


# Inicia el manejador de trabajos de RunPod
logger.info("=== INICIANDO SERVIDOR RUNPOD ===")
logger.info("Configuración:")
logger.info("  - Handler: handler")
logger.info("  - Init: init")
logger.info("Servidor listo para recibir trabajos...")
runpod.serverless.start({"handler": handler, "init": init})
