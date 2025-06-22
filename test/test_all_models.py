#!/usr/bin/env python3
"""
Script para probar automáticamente todos los modelos disponibles en Ollama
Uso: python test_all_models.py
"""

import sys
import time
from typing import List, Dict

# Importar utilidades comunes
try:
    from ollama_test_utils import (
        check_ollama_status, 
        get_available_models, 
        categorize_model, 
        test_single_model, 
        MODEL_TESTS
    )
except ImportError:
    print("❌ Error: No se puede importar ollama_test_utils.py")
    print("   Asegúrate de que el archivo esté en el mismo directorio")
    sys.exit(1)

def main():
    """Función principal"""
    print("🤖 Test Automático de Todos los Modelos")
    print("=" * 50)
    
    # Verificar conexión
    if not check_ollama_status():
        return
    
    # Obtener modelos disponibles
    models = get_available_models()
    if not models:
        print("📋 No hay modelos disponibles")
        print("   Descarga algunos modelos con: ./ollama.sh pull [modelo]")
        return
    
    print(f"📋 Modelos encontrados: {len(models)}")
    for model in models:
        print(f"   • {model}")
    
    # Ejecutar tests
    results = []
    successful_tests = 0
    
    for model_name in models:
        category = categorize_model(model_name)
        
        if category in MODEL_TESTS:
            test_config = MODEL_TESTS[category]
            success = test_single_model(
                model_name, 
                test_config["prompt"], 
                test_config["description"]
            )
        else:
            # Test genérico para modelos no categorizados
            success = test_single_model(
                model_name,
                "Explica brevemente qué es la inteligencia artificial.",
                "Test general"
            )
        
        results.append({
            "model": model_name,
            "category": category,
            "success": success
        })
        
        if success:
            successful_tests += 1
        
        # Pausa entre tests
        time.sleep(1)
    
    # Resumen final
    print("\n" + "=" * 50)
    print("📊 RESUMEN DE TESTS")
    print("=" * 50)
    
    for result in results:
        status = "✅" if result["success"] else "❌"
        print(f"{status} {result['model']} ({result['category']})")
    
    print(f"\n🎯 Resultados: {successful_tests}/{len(results)} tests exitosos")
    
    if successful_tests == len(results):
        print("🎉 ¡Todos los tests pasaron exitosamente!")
    elif successful_tests > 0:
        print("⚠️  Algunos tests fallaron")
    else:
        print("❌ Todos los tests fallaron")

if __name__ == "__main__":
    main() 