# Contenedor Ollama con WebUI en Docker Compose

Este proyecto te permite ejecutar múltiples modelos de IA usando [Ollama](https://ollama.com) en contenedores Docker, incluyendo [OpenCoder](https://github.com/OpenCoder-llm/OpenCoder-llm), [DeepSeek](https://ollama.com/library/deepseek) y [GenAI Image CSPrompt](https://ollama.com/ALIENTELLIGENCE/genaiimagecsprompt), con una interfaz web moderna para gestionar todos los modelos.

## 🚀 Características Principales

- **Arquitectura simplificada**: Un solo servicio Ollama que maneja múltiples modelos
- **Interfaz web moderna**: [Open WebUI](https://github.com/open-webui/open-webui) para gestión visual
- **Múltiples modelos**: Soporte para 3 familias de modelos diferentes

## 🤖 Modelos Disponibles

### OpenCoder
- **Descripción**: Familia de modelos de lenguaje de código abierto y reproducible
- **Modelos**: OpenCoder-1.5B (1.4GB) y OpenCoder-8B (4.7GB)
- **Ventana de contexto**: 4K para 1.5B, 8K para 8B
- **Soporte multilingüe**: Inglés y chino
- **Especialidad**: Generación de código, programación general

### DeepSeek
- **DeepSeek Coder**: Modelo especializado en programación y algoritmos complejos
  - **6.7B**: ~6.7GB, contexto 32K
  - **1.3B**: Modelo ligero para tareas básicas
- **DeepSeek-R1**: Modelo de razonamiento avanzado
  - **1.5B**: 1.1GB, modelo ligero
  - **7B**: 4.7GB, equilibrio rendimiento/tamaño
  - **8B**: 5.2GB, rendimiento mejorado
  - **14B**: 9.0GB, alta precisión
  - **32B**: 20GB, máxima precisión
  - **70B**: 43GB, estado del arte

### GenAI Image CSPrompt
- **Descripción**: Generador de prompts para imágenes de IA
- **Tamaño**: 4.7GB
- **Ventana de contexto**: 8K
- **Especialidad**: Crear prompts detallados para DALL-E, Midjourney, Stable Diffusion

## 📋 Requisitos

- Docker
- Docker Compose
- Al menos 8GB de RAM libre (recomendado 16GB+)
- 20GB de espacio en disco
- Python 3.7+ (para scripts de prueba)

## 🛠️ Instalación y Uso

### 1. Inicio rápido

```bash
# Iniciar servicios básicos
./ollama.sh start

# O iniciar con interfaz web
./ollama.sh start webui
```

### 2. Gestión con el script principal

```bash
# Iniciar servicios
./ollama.sh start              # Solo Ollama
./ollama.sh start webui        # Ollama + interfaz web

# Descargar modelos
./ollama.sh pull opencoder:1.5b
./ollama.sh pull deepseek-coder:6.7b
./ollama.sh pull deepseek-r1:1.5b
./ollama.sh pull alientelligence/genaiimagecsprompt

# Ver logs
./ollama.sh logs ollama
./ollama.sh logs webui

# Probar API
./ollama.sh test

# Ver estado
./ollama.sh status

# Listar modelos
./ollama.sh list

# Detener servicios
./ollama.sh stop
```

### 3. Tests automáticos

```bash
# Probar todos los modelos disponibles
python3 test/test_all_models.py

# Probar modelo específico
python3 test/test_ollama.py
```

## 🌐 Interfaz Web

### Open WebUI
- **URL**: http://localhost:8080
- **Características**:
  - Gestión visual de modelos
  - Chat interactivo con múltiples modelos
  - Configuración de parámetros
  - Historial de conversaciones
  - Gestión de usuarios

### Configuración de variables de entorno

Crea un archivo `.env` en la raíz del proyecto:

```env
OLLAMA_BASE_URL=http://ollama:11434
WEBUI_SECRET_KEY=tu_clave_secreta_aqui
DEFAULT_USER_ROLE=admin
ENABLE_SIGNUP=true
ENABLE_LOGIN_FORM=true
```

## 🔌 Puertos y Servicios

- **Ollama API**: `http://localhost:11434`
- **Open WebUI**: `http://localhost:8080`

## 📝 Ejemplos de Uso

### API REST - OpenCoder

```bash
curl -X POST http://localhost:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "model": "opencoder:8b",
    "prompt": "Escribe una función de ordenamiento rápido en Python",
    "stream": false
  }'
```

### API REST - DeepSeek

```bash
curl -X POST http://localhost:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "model": "deepseek-coder:6.7b",
    "prompt": "Implementa un algoritmo de machine learning completo con visualización",
    "stream": false
  }'
```

### API REST - GenAI Image CSPrompt

```bash
curl -X POST http://localhost:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "model": "alientelligence/genaiimagecsprompt",
    "prompt": "Crea un prompt para generar una imagen de un paisaje de montaña al atardecer",
    "stream": false
  }'
```

## 🧪 Scripts de Prueba

### Test Automático de Modelos

```bash
python3 test/test_all_models.py
```

Este script:
- Detecta automáticamente todos los modelos disponibles
- Ejecuta prompts específicos para cada tipo de modelo
- Muestra métricas de rendimiento (tiempo, tokens)
- Genera un reporte completo de resultados

### Test Individual

```bash
python3 test/test_ollama.py
```

## 📊 Gestión de Modelos

### Listar modelos disponibles
```bash
curl http://localhost:11434/api/tags
```

### Eliminar un modelo
```bash
curl -X DELETE http://localhost:11434/api/delete \
  -H "Content-Type: application/json" \
  -d '{"name": "opencoder:8b"}'
```

### Información del modelo
```bash
curl http://localhost:11434/api/show \
  -H "Content-Type: application/json" \
  -d '{"name": "opencoder:8b"}'
```

## ⚙️ Configuración Avanzada

### Variables de entorno

Puedes modificar las variables de entorno en el `docker-compose.yml`:

- `OLLAMA_HOST`: Host de escucha (por defecto: 0.0.0.0)
- `OLLAMA_ORIGINS`: Orígenes permitidos para CORS

### Volúmenes

Los datos se almacenan en bind mounts para fácil acceso:

- `./data/ollama`: Modelos y configuración de Ollama
- `./data/open-webui`: Datos de la interfaz web

### Recursos del sistema

Para optimizar el rendimiento, puedes agregar límites de recursos:

```yaml
services:
  ollama:
    # ... configuración existente ...
    deploy:
      resources:
        limits:
          memory: 16G
          cpus: '8.0'
        reservations:
          memory: 8G
          cpus: '4.0'
```

## 🔧 Solución de Problemas

### El contenedor no inicia

1. Verifica que tienes suficiente espacio en disco
2. Asegúrate de que los puertos no estén en uso
3. Revisa los logs: `./ollama.sh logs ollama`

### Error de memoria

Si obtienes errores de memoria insuficiente:

1. Reduce el número de modelos ejecutándose simultáneamente
2. Usa solo modelos más pequeños (OpenCoder 1.5B, DeepSeek-R1 1.5B)
3. Aumenta la memoria disponible para Docker

### Modelo no responde

1. Verifica que el modelo se descargó correctamente: `./ollama.sh list`
2. Revisa los logs del contenedor: `./ollama.sh logs ollama`
3. Intenta reiniciar el servicio: `./ollama.sh restart`

### Problemas con la interfaz web

1. Verifica que las variables de entorno están configuradas correctamente
2. Revisa los logs: `./ollama.sh logs webui`
3. Asegúrate de que Ollama está ejecutándose antes de iniciar la web UI

## 📈 Comparación de Modelos

| Modelo | Tamaño | Contexto | Especialidad | Uso Recomendado |
|--------|--------|----------|--------------|-----------------|
| OpenCoder 1.5B | 1.4GB | 4K | Código general | Desarrollo rápido |
| OpenCoder 8B | 4.7GB | 8K | Código avanzado | Proyectos complejos |
| DeepSeek Coder 1.3B | ~1GB | 4K | Programación básica | Aprendizaje |
| DeepSeek Coder 6.7B | 6.7GB | 32K | Algoritmos complejos | ML, optimización |
| DeepSeek-R1 1.5B | 1.1GB | 4K | Razonamiento básico | Lógica simple |
| DeepSeek-R1 8B | 5.2GB | 8K | Razonamiento avanzado | Problemas complejos |
| DeepSeek-R1 32B | 20GB | 32K | Máxima precisión | Investigación |
| GenAI Image CSPrompt | 4.7GB | 8K | Prompts para imágenes | Generación de contenido |

## 📚 Referencias

- [Repositorio de OpenCoder](https://github.com/OpenCoder-llm/OpenCoder-llm)
- [DeepSeek en Ollama](https://ollama.com/library/deepseek)
- [GenAI Image CSPrompt en Ollama](https://ollama.com/ALIENTELLIGENCE/genaiimagecsprompt)
- [Open WebUI](https://github.com/open-webui/open-webui)
- [Documentación de Ollama](https://ollama.com/docs)
- [Paper de OpenCoder](https://arxiv.org/pdf/2411.04905)

## 📄 Licencia

Este proyecto está bajo la licencia MIT, al igual que los modelos incluidos.


