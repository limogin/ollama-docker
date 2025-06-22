#!/usr/bin/env python3
"""
Utilidades comunes para testing de Ollama
Módulo compartido entre test_all_models.py y test_ollama.py
"""

import requests
import time
from typing import List, Dict, Any, Optional

# Configuración
OLLAMA_BASE_URL = "http://localhost:11434"

# Prompts específicos para cada tipo de modelo
MODEL_TESTS = {
    "opencoder": {
        "prompt": "Escribe una función en Python que implemente el algoritmo de ordenamiento quicksort.",
        "description": "Test de programación"
    },
    "deepseek-coder": {
        "prompt": "Explica cómo funciona la recursión en programación y da un ejemplo práctico.",
        "description": "Test de programación"
    },
    "deepseek-r1": {
        "prompt": "Si un tren sale de Madrid a las 10:00 AM y viaja a 120 km/h, y otro tren sale de Barcelona a las 11:00 AM hacia Madrid a 100 km/h, ¿a qué hora se encontrarán si la distancia entre las ciudades es de 500 km? Explica tu razonamiento paso a paso.",
        "description": "Test de razonamiento matemático"
    },
    "genaiimagecsprompt": {
        "prompt": "Genera un prompt detallado para crear una imagen de un robot chef cocinando en una cocina futurista con elementos steampunk.",
        "description": "Test de generación de prompts para imágenes"
    }
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

def get_available_models() -> List[str]:
    """Obtener lista de modelos disponibles"""
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=10)
        if response.status_code == 200:
            models = response.json().get("models", [])
            return [model.get("name") for model in models]
        else:
            print(f"❌ Error al obtener modelos: {response.status_code}")
            return []
    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión: {e}")
        return []

def list_available_models() -> List[str]:
    """Listar modelos disponibles en Ollama con información detallada"""
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

def categorize_model(model_name: str) -> str:
    """Categorizar un modelo basado en su nombre"""
    if "opencoder" in model_name:
        return "opencoder"
    elif "deepseek-coder" in model_name:
        return "deepseek-coder"
    elif "deepseek-r1" in model_name:
        return "deepseek-r1"
    elif "genaiimagecsprompt" in model_name:
        return "genaiimagecsprompt"
    else:
        return "general"

def test_single_model(model_name: str, prompt: str, description: str, max_tokens: int = 300) -> bool:
    """Probar un modelo individual"""
    print(f"\n🤖 Probando: {model_name}")
    print(f"📝 Tipo: {description}")
    print(f"📋 Prompt: {prompt[:80]}{'...' if len(prompt) > 80 else ''}")
    print("-" * 60)
    
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
            timeout=180  # 3 minutos
        )
        end_time = time.time()
        
        if response.status_code == 200:
            result = response.json()
            response_text = result.get("response", "")
            total_duration = result.get("total_duration", 0) / 1e9
            
            print(f"✅ Respuesta ({total_duration:.2f}s):")
            print(response_text[:200] + "..." if len(response_text) > 200 else response_text)
            print(f"\n⏱️  Tiempo: {total_duration:.2f}s")
            print(f"📊 Tokens: {result.get('eval_count', 0)}")
            return True
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Timeout")
        return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Error: {e}")
        return False

def test_model(model_name: str, prompt: str, max_tokens: int = 500) -> bool:
    """Probar un modelo específico con un prompt (versión completa)"""
    print(f"\n🤖 Probando modelo: {model_name}")
    print(f"📝 Prompt: {prompt[:100]}{'...' if len(prompt) > 100 else ''}")
    print("-" * 60)
    
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
            total_duration = result.get("total_duration", 0) / 1e9
            
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