#!/usr/bin/env python3
"""
Script de prueba para Qwen-Image-Edit usando CPU
Optimizado para sistemas sin GPU NVIDIA
"""

import torch
import time
from diffusers import QwenImageEditPipeline
from PIL import Image
import sys

def cpu_test():
    """Prueba del pipeline usando CPU"""
    
    print("=== PRUEBA QWEN-IMAGE-EDIT EN CPU ===")
    print("⚠️  Advertencia: Usando CPU - será mucho más lento")
    
    # Forzar uso de CPU
    device = "cpu"
    torch_dtype = torch.float32  # CPU necesita float32
    
    print(f"Dispositivo: {device}")
    print(f"Tipo de datos: {torch_dtype}")
    
    try:
        print("\n🔨 Cargando pipeline en CPU...")
        start_time = time.time()
        
        # Cargar pipeline con configuración para CPU
        pipeline = QwenImageEditPipeline.from_pretrained(
            "Qwen/Qwen-Image-Edit",
            torch_dtype=torch_dtype,
            low_cpu_mem_usage=True,
            use_safetensors=True
        ).to(device)
        
        load_time = time.time() - start_time
        print(f"✅ Pipeline cargado en {load_time:.2f} segundos")
        
        # Crear imagen de prueba más pequeña para CPU
        print("\n🖼️  Creando imagen de prueba (256x256)...")
        test_image = Image.new('RGB', (256, 256), color='lightblue')
        test_mask = Image.new('RGB', (256, 256), color='black')
        
        # Probar inferencia con configuración mínima
        print("🚀 Probando inferencia en CPU...")
        prompt = "A simple mountain landscape"
        
        inference_start = time.time()
        result = pipeline(
            prompt=prompt,
            image=test_image,
            mask_image=test_mask,
            guidance_scale=7.5,
            num_inference_steps=5  # Muy pocos steps para CPU
        )
        
        inference_time = time.time() - inference_start
        print(f"✅ Inferencia completada en {inference_time:.2f} segundos")
        
        if result.images and len(result.images) > 0:
            output_image = result.images[0]
            print(f"✅ Imagen generada: {output_image.size} ({output_image.mode})")
            
            # Guardar resultado
            output_image.save("cpu_test_result.png")
            print("💾 Imagen guardada como 'cpu_test_result.png'")
            
            print("\n🎉 ¡PRUEBA EXITOSA EN CPU!")
            print("⚠️  Nota: La calidad puede ser menor debido a los pocos steps")
            return True
        else:
            print("❌ No se generó ninguna imagen")
            return False
            
    except Exception as e:
        print(f"❌ Error durante la prueba: {str(e)}")
        print("💡 Sugerencia: El modelo puede ser demasiado grande para CPU")
        return False
    finally:
        # Limpiar memoria
        if 'pipeline' in locals():
            del pipeline
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

if __name__ == "__main__":
    success = cpu_test()
    sys.exit(0 if success else 1)
