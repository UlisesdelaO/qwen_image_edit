#!/usr/bin/env python3
"""
Script de prueba rápida para Qwen-Image-Edit
Ejecuta una prueba básica sin interfaz gráfica
"""

import torch
import time
from diffusers import QwenImageEditPipeline
from PIL import Image
import sys

def quick_test():
    """Prueba rápida del pipeline"""
    
    print("=== PRUEBA RÁPIDA QWEN-IMAGE-EDIT ===")
    
    # Verificar CUDA
    if not torch.cuda.is_available():
        print("❌ CUDA no está disponible")
        return False
    
    print(f"✅ GPU: {torch.cuda.get_device_name(0)}")
    print(f"✅ VRAM: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
    
    # Verificar memoria suficiente
    vram_gb = torch.cuda.get_device_properties(0).total_memory / 1024**3
    if vram_gb < 20:
        print(f"⚠️  Advertencia: Solo {vram_gb:.1f}GB VRAM disponible. Se recomiendan 20GB+")
        print("   El modelo puede no cargar correctamente.")
    
    try:
        print("\n🔨 Cargando pipeline...")
        start_time = time.time()
        
        # Cargar pipeline con optimizaciones
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
        print(f"✅ Pipeline cargado en {load_time:.2f} segundos")
        
        # Crear imagen de prueba
        print("\n🖼️  Creando imagen de prueba...")
        test_image = Image.new('RGB', (512, 512), color='lightblue')
        test_mask = Image.new('RGB', (512, 512), color='black')
        
        # Probar inferencia rápida
        print("🚀 Probando inferencia...")
        prompt = "A beautiful mountain landscape with a lake"
        
        inference_start = time.time()
        result = pipeline(
            prompt=prompt,
            image=test_image,
            mask_image=test_mask,
            guidance_scale=7.5,
            num_inference_steps=10  # Menos steps para prueba rápida
        )
        
        inference_time = time.time() - inference_start
        print(f"✅ Inferencia completada en {inference_time:.2f} segundos")
        
        if result.images and len(result.images) > 0:
            output_image = result.images[0]
            print(f"✅ Imagen generada: {output_image.size} ({output_image.mode})")
            
            # Guardar resultado
            output_image.save("quick_test_result.png")
            print("💾 Imagen guardada como 'quick_test_result.png'")
            
            # Mostrar estadísticas de memoria
            if torch.cuda.is_available():
                print(f"\n📊 Estadísticas de memoria:")
                print(f"   VRAM usada: {torch.cuda.memory_allocated(0) / 1024**3:.1f} GB")
                print(f"   VRAM reservada: {torch.cuda.memory_reserved(0) / 1024**3:.1f} GB")
            
            print("\n🎉 ¡PRUEBA EXITOSA!")
            return True
        else:
            print("❌ No se generó ninguna imagen")
            return False
            
    except torch.cuda.OutOfMemoryError as e:
        print(f"❌ Error de memoria CUDA: {str(e)}")
        print("   Necesitas al menos 20GB de VRAM para este modelo")
        return False
    except Exception as e:
        print(f"❌ Error durante la prueba: {str(e)}")
        return False
    finally:
        # Limpiar memoria
        if 'pipeline' in locals():
            del pipeline
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

if __name__ == "__main__":
    success = quick_test()
    sys.exit(0 if success else 1)
