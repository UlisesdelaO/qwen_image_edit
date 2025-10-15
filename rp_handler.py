# rp_handler.py
# Qwen-Image-Edit RunPod Serverless Handler
# Updated: October 12, 2025 - Using official QwenImageEditPipeline
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

# Configurar logging detallado para RunPod
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('qwen_image_edit.log')
    ]
)
logger = logging.getLogger(__name__)

# Configurar logging específico para RunPod
runpod_logger = logging.getLogger('runpod')
runpod_logger.setLevel(logging.INFO)

# Logger para métricas de rendimiento
metrics_logger = logging.getLogger('metrics')
metrics_logger.setLevel(logging.INFO)

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
        # Log de información del sistema
        logger.info("=== INFORMACIÓN DEL SISTEMA ===")
        logger.info(f"PyTorch version: {torch.__version__}")
        logger.info(f"CUDA disponible: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            logger.info(f"CUDA version: {torch.version.cuda}")
            logger.info(f"GPU: {torch.cuda.get_device_name(0)}")
            logger.info(f"VRAM total: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
            logger.info(f"VRAM libre: {(torch.cuda.get_device_properties(0).total_memory - torch.cuda.memory_allocated(0)) / 1024**3:.1f} GB")
        
        logger.info("Limpiando caché de CUDA...")
        torch.cuda.empty_cache()
        logger.info("Caché de CUDA limpiado exitosamente")

        logger.info("=== INICIANDO CARGA DEL PIPELINE ===")
        logger.info("Modelo: Qwen-Image-Edit (20B MMDiT)")
        logger.info("Tipo de datos: torch.float16")
        logger.info("Dispositivo: CUDA")
        logger.info("Optimizaciones: memory_efficient_attention, model_cpu_offload")
        
        # Cargar el pipeline oficial de Qwen-Image-Edit
        pipeline = QwenImageEditPipeline.from_pretrained(
            "Qwen/Qwen-Image-Edit",
            torch_dtype=torch.float16,
            low_cpu_mem_usage=True,
            use_safetensors=True
        ).to("cuda")
        
        # Habilitar optimizaciones de memoria
        logger.info("Aplicando optimizaciones de memoria...")
        pipeline.enable_memory_efficient_attention()
        pipeline.enable_model_cpu_offload()
        logger.info("Optimizaciones aplicadas exitosamente")

        load_time = time.time() - start_time
        logger.info(f"=== CARGA COMPLETADA ===")
        logger.info(f"Tiempo total de carga: {load_time:.2f} segundos")
        
        # Log de memoria después de la carga
        if torch.cuda.is_available():
            logger.info(f"VRAM usada después de carga: {torch.cuda.memory_allocated(0) / 1024**3:.1f} GB")
            logger.info(f"VRAM reservada: {torch.cuda.memory_reserved(0) / 1024**3:.1f} GB")
            logger.info(f"VRAM libre restante: {(torch.cuda.get_device_properties(0).total_memory - torch.cuda.memory_allocated(0)) / 1024**3:.1f} GB")
        
        logger.info("Pipeline inicializado y listo para procesar imágenes")
        logger.info("=== CARGA DEL MODELO COMPLETADA EXITOSAMENTE ===")
        
        return pipeline
        
    except Exception as e:
        load_time = time.time() - start_time
        logger.error(f"=== ERROR DURANTE LA CARGA DEL MODELO ===")
        logger.error(f"Tiempo transcurrido antes del error: {load_time:.2f} segundos")
        logger.error(f"Error: {str(e)}")
        logger.error(f"Tipo de error: {type(e).__name__}")
        logger.error(f"Traceback completo: {traceback.format_exc()}")
        
        # Log de memoria en caso de error
        if torch.cuda.is_available():
            logger.error(f"VRAM disponible en el momento del error: {(torch.cuda.get_device_properties(0).total_memory - torch.cuda.memory_allocated(0)) / 1024**3:.1f} GB")
        
        logger.error("=== FALLO EN CARGA DEL MODELO ===")
        # No hacer raise para evitar que el worker falle completamente
        return None


def handler(job):
    """
    Esta función se ejecuta por cada llamada a la API.
    Procesa la entrada y devuelve la imagen generada.
    """
    request_id = f"req_{int(time.time() * 1000)}"
    logger.info(f"=== INICIANDO PROCESAMIENTO DE TRABAJO [{request_id}] ===")
    start_time = time.time()
    
    try:
        # Log de información del job
        logger.info(f"Job ID: {job.get('id', 'N/A')}")
        logger.info(f"Request ID: {request_id}")
        logger.info(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        global pipeline
        if pipeline is None:
            logger.warning("Pipeline no inicializado, ejecutando init()...")
            pipeline = init()
            if pipeline is None:
                logger.error("No se pudo inicializar el pipeline")
                return {"error": "Error interno: No se pudo cargar el modelo"}
        else:
            logger.info("Pipeline ya está inicializado, continuando...")

        logger.info("=== VALIDACIÓN DE ENTRADA ===")
        # Valida la entrada del trabajo contra el esquema
        validated_input = validate(job['input'], INPUT_SCHEMA)
        if 'errors' in validated_input:
            logger.error(f"Errores de validación encontrados: {validated_input['errors']}")
            return {"error": validated_input['errors']}
        
        logger.info("Entrada validada exitosamente")
        job_input = validated_input['validated_input']
        
        logger.info(f"Prompt recibido: {job_input['prompt'][:100]}...")
        logger.info(f"Tamaño de imagen del usuario: {len(job_input['user_image'])} caracteres en base64")
        
        logger.info("=== PROCESAMIENTO DE IMÁGENES ===")
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

        logger.info("=== EJECUCIÓN DEL PIPELINE ===")
        logger.info("Parámetros de inferencia:")
        logger.info(f"  - Prompt: {job_input['prompt'][:50]}...")
        logger.info(f"  - Guidance scale: 7.5")
        logger.info(f"  - Inference steps: 20")
        logger.info(f"  - Máscara: {'Sí' if mask_image else 'No'}")
        logger.info(f"  - Tamaño de imagen: {user_image.size}")
        
        # Log de memoria antes de la inferencia
        if torch.cuda.is_available():
            logger.info(f"VRAM antes de inferencia: {torch.cuda.memory_allocated(0) / 1024**3:.1f} GB")
        
        pipeline_start = time.time()
        # Ejecuta el pipeline de edición con Qwen-Image-Edit
        result_image = pipeline(
            prompt=job_input['prompt'],
            image=user_image,
            mask_image=mask_image if mask_image else Image.new('RGB', user_image.size, (0, 0, 0)),
            guidance_scale=7.5,
            num_inference_steps=20
        ).images[0]
        
        pipeline_time = time.time() - pipeline_start
        logger.info(f"Pipeline ejecutado exitosamente en {pipeline_time:.2f} segundos")
        logger.info(f"Imagen resultante: {result_image.size} ({result_image.mode})")

        # Log de memoria después de la inferencia
        if torch.cuda.is_available():
            logger.info(f"VRAM después de inferencia: {torch.cuda.memory_allocated(0) / 1024**3:.1f} GB")

        logger.info("=== CONVERSIÓN DE RESULTADO ===")
        logger.info("Convirtiendo imagen resultante a base64...")
        # Convierte la imagen de resultado a base64 para devolverla en la respuesta JSON
        buffered = BytesIO()
        result_image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
        logger.info(f"Imagen convertida a base64: {len(img_str)} caracteres")

        total_time = time.time() - start_time
        logger.info(f"=== PROCESAMIENTO COMPLETADO ===")
        logger.info(f"Tiempo total: {total_time:.2f} segundos")
        logger.info(f"Tiempo de pipeline: {pipeline_time:.2f} segundos")
        logger.info(f"Tiempo de procesamiento: {total_time - pipeline_time:.2f} segundos")
        logger.info(f"Request ID: {request_id}")
        logger.info("=== PROCESAMIENTO DE TRABAJO COMPLETADO EXITOSAMENTE ===")

        # Log de métricas para RunPod
        metrics_logger.info(f"METRICS: {request_id} | Total: {total_time:.2f}s | Pipeline: {pipeline_time:.2f}s | Success: True")

        # Devuelve la imagen como una cadena base64
        return {"image_base64": img_str}
        
    except Exception as e:
        total_time = time.time() - start_time
        logger.error(f"=== ERROR DURANTE EL PROCESAMIENTO ===")
        logger.error(f"Request ID: {request_id}")
        logger.error(f"Tiempo transcurrido antes del error: {total_time:.2f} segundos")
        logger.error(f"Error: {str(e)}")
        logger.error(f"Tipo de error: {type(e).__name__}")
        logger.error(f"Traceback completo: {traceback.format_exc()}")
        
        # Log de memoria en caso de error
        if torch.cuda.is_available():
            logger.error(f"VRAM en el momento del error: {torch.cuda.memory_allocated(0) / 1024**3:.1f} GB")
        
        # Log de métricas de error
        metrics_logger.error(f"METRICS: {request_id} | Total: {total_time:.2f}s | Success: False | Error: {type(e).__name__}")
        
        logger.error("=== PROCESAMIENTO DE TRABAJO FALLÓ ===")
        return {"error": f"Error interno del servidor: {str(e)}"}


# Inicia el manejador de trabajos de RunPod
logger.info("=== INICIANDO SERVIDOR RUNPOD ===")
logger.info("Configuración:")
logger.info("  - Handler: handler")
logger.info("  - Init: init")
logger.info("Servidor listo para recibir trabajos...")
runpod.serverless.start({"handler": handler, "init": init})
