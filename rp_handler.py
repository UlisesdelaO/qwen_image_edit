# rp_handler.py
import runpod
import torch
from diffusers import QwenImageEditPipeline
from runpod.serverless.utils.rp_validator import validate
from PIL import Image
import base64
from io import BytesIO

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
    global pipeline
    torch.cuda.empty_cache()

    # Carga el pipeline de Qwen-Image-Edit
    pipeline = QwenImageEditPipeline.from_pretrained(
        "Qwen/Qwen-Image-Edit",
        torch_dtype=torch.float16,
        low_cpu_mem_usage=False
    ).to("cuda")

    print("Pipeline inicializado y listo.")
    return pipeline


def handler(job):
    """
    Esta función se ejecuta por cada llamada a la API.
    Procesa la entrada y devuelve la imagen generada.
    """
    global pipeline
    if pipeline is None:
        pipeline = init()

    # Valida la entrada del trabajo contra el esquema
    validated_input = validate(job['input'], INPUT_SCHEMA)
    if 'errors' in validated_input:
        return {"error": validated_input['errors']}
    
    job_input = validated_input['validated_input']

    # Decodificar la imagen del usuario de base64 a PIL.Image
    user_img_bytes = base64.b64decode(job_input['user_image'])
    user_image = Image.open(BytesIO(user_img_bytes))

    # Decodificar la máscara si se proporciona
    mask_image = None
    if job_input.get('mask_image'):
        mask_img_bytes = base64.b64decode(job_input['mask_image'])
        mask_image = Image.open(BytesIO(mask_img_bytes))

    # Ejecuta el pipeline de edición
    # Nota: Aquí puedes usar la 'plantilla' como 'user_image' y la 'foto de perfil' 
    # en el prompt o como otra entrada, dependiendo de tu lógica exacta.
    # Este es un ejemplo de edición general.
    result_image = pipeline(
        prompt=job_input['prompt'],
        image=user_image,
        mask_image=mask_image, # mask_image es opcional
        strength=0.9,
        guidance_scale=7.5
    ).images[0]

    # Convierte la imagen de resultado a base64 para devolverla en la respuesta JSON
    buffered = BytesIO()
    result_image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")

    # Devuelve la imagen como una cadena base64
    return {"image_base64": img_str}


# Inicia el manejador de trabajos de RunPod
runpod.serverless.start({"handler": handler, "init": init})
