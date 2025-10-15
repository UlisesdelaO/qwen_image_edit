#!/usr/bin/env python3
"""
Script de prueba para Qwen-Image-Edit
Prueba la funcionalidad básica del pipeline antes del despliegue
"""

import torch
from diffusers import QwenImageEditPipeline
from PIL import Image
import base64
from io import BytesIO
import time
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_qwen_image_edit():
    """Prueba básica del pipeline de Qwen-Image-Edit"""
    
    logger.info("=== INICIANDO PRUEBA DE QWEN-IMAGE-EDIT ===")
    
    try:
        # Verificar CUDA
        if not torch.cuda.is_available():
            logger.error("CUDA no está disponible")
            return False
            
        logger.info(f"CUDA disponible: {torch.cuda.get_device_name(0)}")
        logger.info(f"VRAM disponible: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
        
        # Cargar pipeline
        logger.info("Cargando Qwen-Image-Edit pipeline...")
        start_time = time.time()
        
        pipeline = QwenImageEditPipeline.from_pretrained(
            "Qwen/Qwen-Image-Edit",
            torch_dtype=torch.float16,
            low_cpu_mem_usage=True,
            use_safetensors=True
        ).to("cuda")
        
        # Optimizaciones
        pipeline.enable_memory_efficient_attention()
        pipeline.enable_model_cpu_offload()
        
        load_time = time.time() - start_time
        logger.info(f"Pipeline cargado en {load_time:.2f} segundos")
        
        # Crear imagen de prueba
        logger.info("Creando imagen de prueba...")
        test_image = Image.new('RGB', (512, 512), color='red')
        
        # Crear máscara de prueba
        mask_image = Image.new('RGB', (512, 512), color='black')
        
        # Probar inferencia
        logger.info("Probando inferencia...")
        prompt = "A beautiful landscape with mountains and a lake"
        
        inference_start = time.time()
        result = pipeline(
            prompt=prompt,
            image=test_image,
            mask_image=mask_image,
            guidance_scale=7.5,
            num_inference_steps=20
        )
        
        inference_time = time.time() - inference_start
        logger.info(f"Inferencia completada en {inference_time:.2f} segundos")
        
        # Verificar resultado
        if result.images and len(result.images) > 0:
            output_image = result.images[0]
            logger.info(f"Imagen generada: {output_image.size} ({output_image.mode})")
            
            # Guardar imagen de prueba
            output_image.save("test_output.png")
            logger.info("Imagen de prueba guardada como 'test_output.png'")
            
            logger.info("=== PRUEBA EXITOSA ===")
            return True
        else:
            logger.error("No se generó ninguna imagen")
            return False
            
    except Exception as e:
        logger.error(f"Error durante la prueba: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    import traceback
    success = test_qwen_image_edit()
    exit(0 if success else 1)
