#!/usr/bin/env python3
"""
Script unificado para probar modelos de Ollama
Uso: python test_ollama.py [modelo] [prompt]
"""

import requests
import json
import sys
import time
from typing import Dict, Any, Optional

# Configuración
OLLAMA_BASE_URL = "http://localhost:11434"
DEFAULT_MODEL = "deepseek-r1:1.5b"  # Modelo por defecto

# Modelos disponibles para testing
AVAILABLE_MODELS = {
    "opencoder-8b": "opencoder:8b",
    "opencoder-1.5b": "opencoder:1.5b", 
    "deepseek-coder-6.7b": "deepseek-coder:6.7b",
    "deepseek-coder-1.3b": "deepseek-coder:1.3b",
    "deepseek-r1": "deepseek-r1",
    "deepseek-r1-1.5b": "deepseek-r1:1.5b",
    "deepseek-r1-7b": "deepseek-r1:7b",
    "deepseek-r1-8b": "deepseek-r1:8b",
    "deepseek-r1-14b": "deepseek-r1:14b",
    "deepseek-r1-32b": "deepseek-r1:32b",
    "deepseek-r1-70b": "deepseek-r1:70b",
    "genaiimagecsprompt": "alientelligence/genaiimagecsprompt"
}

# Prompts de ejemplo para diferentes tipos de modelos
EXAMPLE_PROMPTS = {
    "coding": "Escribe una función en Python que calcule el factorial de un número usando recursión.",
    "reasoning": "Si tengo 3 manzanas y me como 1, luego compro 2 más, ¿cuántas manzanas tengo? Explica tu razonamiento paso a paso.",
    "image_prompt": "Genera un prompt detallado para crear una imagen de un gato espacial viajando en una nave espacial futurista.",
    "general": "Explica brevemente qué es la inteligencia artificial y sus aplicaciones principales."
}

def check_ollama_status() -> bool:
    """Verificar si Ollama está ejecutándose"""
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/version", timeout=5)
        if response.status_code == 200:
            version = response.json().get("version", "unknown")
            print(f"✅ Ollama está ejecutándose (versión: {version})")
            return True
        else:
            print(f"❌ Error al conectar con Ollama: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ No se puede conectar con Ollama: {e}")
        print(f"   Asegúrate de que Ollama esté ejecutándose en {OLLAMA_BASE_URL}")
        return False

def list_available_models() -> list:
    """Listar modelos disponibles en Ollama"""
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=10)
        if response.status_code == 200:
            models = response.json().get("models", [])
            if models:
                print("📋 Modelos disponibles:")
                for model in models:
                    name = model.get("name", "unknown")
                    size = model.get("size", 0)
                    size_gb = size / (1024**3) if size > 0 else 0
                    print(f"   • {name} ({size_gb:.1f}GB)")
                return [model.get("name") for model in models]
            else:
                print("📋 No hay modelos descargados")
                return []
        else:
            print(f"❌ Error al obtener modelos: {response.status_code}")
            return []
    except requests.exceptions.RequestException as e:
        print(f"❌ Error al conectar con Ollama: {e}")
        return []

def test_model(model_name: str, prompt: str, max_tokens: int = 500) -> bool:
    """Probar un modelo específico con un prompt"""
    print(f"\n🤖 Probando modelo: {model_name}")
    print(f"📝 Prompt: {prompt[:100]}{'...' if len(prompt) > 100 else ''}")
    print("-" * 60)
    
    # Preparar la solicitud
    payload = {
        "model": model_name,
        "prompt": prompt,
        "stream": False,
        "options": {
            "num_predict": max_tokens,
            "temperature": 0.7,
            "top_p": 0.9
        }
    }
    
    try:
        start_time = time.time()
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json=payload,
            timeout=120  # 2 minutos de timeout
        )
        end_time = time.time()
        
        if response.status_code == 200:
            result = response.json()
            response_text = result.get("response", "")
            total_duration = result.get("total_duration", 0) / 1e9  # Convertir a segundos
            
            print(f"✅ Respuesta ({total_duration:.2f}s):")
            print(response_text)
            print(f"\n⏱️  Tiempo total: {total_duration:.2f}s")
            print(f"📊 Tokens generados: {result.get('eval_count', 0)}")
            return True
        else:
            error_msg = response.text
            print(f"❌ Error en la respuesta: {response.status_code}")
            print(f"   Detalles: {error_msg}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Timeout: La respuesta tardó demasiado")
        return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión: {e}")
        return False

def test_image_generation(model_name: str, prompt: str) -> bool:
    """Probar generación de imágenes (para modelos como SDXL)"""
    print(f"\n🎨 Probando generación de imagen con: {model_name}")
    print(f"📝 Prompt: {prompt}")
    print("-" * 60)
    
    payload = {
        "model": model_name,
        "prompt": prompt,
        "stream": False
    }
    
    try:
        start_time = time.time()
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json=payload,
            timeout=300  # 5 minutos para generación de imágenes
        )
        end_time = time.time()
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Imagen generada exitosamente")
            print(f"⏱️  Tiempo: {end_time - start_time:.2f}s")
            return True
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error: {e}")
        return False

def show_help():
    """Mostrar ayuda del script"""
    print("""
🤖 Test Unificado de Ollama
==========================

Uso: python test_ollama.py [modelo] [prompt]

Argumentos:
  modelo    Nombre del modelo a probar (opcional)
  prompt    Prompt personalizado (opcional)

Modelos disponibles:
  opencoder-8b          - OpenCoder 8B (código)
  opencoder-1.5b        - OpenCoder 1.5B (código ligero)
  deepseek-coder-6.7b   - DeepSeek Coder 6.7B
  deepseek-coder-1.3b   - DeepSeek Coder 1.3B
  deepseek-r1           - DeepSeek-R1 (razonamiento)
  deepseek-r1-1.5b      - DeepSeek-R1 1.5B (razonamiento ligero)
  deepseek-r1-7b        - DeepSeek-R1 7B
  deepseek-r1-8b        - DeepSeek-R1 8B
  deepseek-r1-14b       - DeepSeek-R1 14B
  deepseek-r1-32b       - DeepSeek-R1 32B
  deepseek-r1-70b       - DeepSeek-R1 70B
  genaiimagecsprompt    - Generador de prompts para imágenes

Ejemplos:
  python test_ollama.py
  python test_ollama.py deepseek-r1-1.5b
  python test_ollama.py opencoder-1.5b "Escribe una función de Fibonacci"
  python test_ollama.py genaiimagecsprompt "gato espacial"
""")

def main():
    """Función principal"""
    print("🤖 Test Unificado de Ollama")
    print("=" * 40)
    
    # Verificar argumentos
    if len(sys.argv) > 1 and sys.argv[1] in ["-h", "--help", "help"]:
        show_help()
        return
    
    # Verificar estado de Ollama
    if not check_ollama_status():
        return
    
    # Listar modelos disponibles
    available_models = list_available_models()
    
    # Determinar modelo a usar
    if len(sys.argv) > 1:
        model_key = sys.argv[1]
        if model_key in AVAILABLE_MODELS:
            model_name = AVAILABLE_MODELS[model_key]
        else:
            print(f"❌ Modelo '{model_key}' no reconocido")
            print("   Usa 'python test_ollama.py help' para ver modelos disponibles")
            return
    else:
        model_name = DEFAULT_MODEL
        print(f"📋 Usando modelo por defecto: {model_name}")
    
    # Verificar si el modelo está disponible
    if model_name not in available_models:
        print(f"⚠️  Modelo '{model_name}' no está descargado")
        print(f"   Descárgalo con: ./ollama.sh pull {model_name}")
        return
    
    # Determinar prompt a usar
    if len(sys.argv) > 2:
        prompt = " ".join(sys.argv[2:])
    else:
        # Seleccionar prompt basado en el tipo de modelo
        if "coder" in model_name or "opencoder" in model_name:
            prompt = EXAMPLE_PROMPTS["coding"]
        elif "r1" in model_name:
            prompt = EXAMPLE_PROMPTS["reasoning"]
        elif "genaiimagecsprompt" in model_name:
            prompt = EXAMPLE_PROMPTS["image_prompt"]
        else:
            prompt = EXAMPLE_PROMPTS["general"]
    
    # Ejecutar test
    if "genaiimagecsprompt" in model_name:
        success = test_image_generation(model_name, prompt)
    else:
        success = test_model(model_name, prompt)
    
    if success:
        print("\n✅ Test completado exitosamente!")
    else:
        print("\n❌ Test falló")
        sys.exit(1)

if __name__ == "__main__":
    main() 