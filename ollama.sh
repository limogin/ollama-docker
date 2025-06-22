#!/bin/bash

# Script para gestionar Ollama con múltiples modelos
# Uso: ./ollama.sh [comando] [opción]

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para mostrar ayuda
show_help() {
    echo -e "${BLUE}Ollama Docker Manager${NC}"
    echo ""
    echo "Uso: $0 [comando] [opción]"
    echo ""
    echo "Comandos:"
    echo "  start [webui]           - Iniciar Ollama (default: solo Ollama)"
    echo "  stop                    - Detener todos los servicios"
    echo "  restart [webui]         - Reiniciar servicios"
    echo "  logs [ollama|webui]     - Mostrar logs (default: ollama)"
    echo "  status                  - Mostrar estado de los contenedores"
    echo "  test                    - Probar la API de Ollama"
    echo "  pull [modelo]           - Descargar modelo específico"
    echo "  list                    - Listar modelos disponibles"
    echo "  clean                   - Limpiar contenedores y datos"
    echo "  help                    - Mostrar esta ayuda"
    echo ""
    echo "Modelos disponibles:"
    echo "  opencoder:8b            - OpenCoder 8B (modelo de código)"
    echo "  opencoder:1.5b          - OpenCoder 1.5B (modelo ligero)"
    echo "  deepseek-coder:6.7b     - DeepSeek Coder 6.7B"
    echo "  deepseek-coder:1.3b     - DeepSeek Coder 1.3B"
    echo "  deepseek-r1             - DeepSeek-R1 (modelo de razonamiento, 5.2GB)"
    echo "  deepseek-r1:1.5b        - DeepSeek-R1 1.5B (modelo ligero, 1.1GB)"
    echo "  deepseek-r1:7b          - DeepSeek-R1 7B (4.7GB)"
    echo "  deepseek-r1:8b          - DeepSeek-R1 8B (5.2GB)"
    echo "  deepseek-r1:14b         - DeepSeek-R1 14B (9.0GB)"
    echo "  deepseek-r1:32b         - DeepSeek-R1 32B (20GB)"
    echo "  deepseek-r1:70b         - DeepSeek-R1 70B (43GB)"
    echo "  alientelligence/genaiimagecsprompt - Generador de prompts para imágenes"
    echo ""
    echo "Ejemplos:"
    echo "  $0 start                # Iniciar solo Ollama"
    echo "  $0 start webui          # Iniciar Ollama + interfaz web"
    echo "  $0 pull opencoder:1.5b  # Descargar modelo OpenCoder 1.5B"
    echo "  $0 pull deepseek-coder:6.7b  # Descargar modelo DeepSeek Coder"
    echo "  $0 pull deepseek-r1     # Descargar modelo DeepSeek-R1 (5.2GB)"
    echo "  $0 pull deepseek-r1:1.5b # Descargar modelo DeepSeek-R1 1.5B (ligero)"
    echo "  $0 list                 # Ver modelos disponibles"
    echo "  $0 test                 # Probar la API"
    echo ""
    echo "Interfaz web:"
    echo "  - Open WebUI: http://localhost:8080"
    echo ""
    echo "API de Ollama:"
    echo "  - Puerto: http://localhost:11434"
}

# Función para verificar si Docker está ejecutándose
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        echo -e "${RED}Error: Docker no está ejecutándose${NC}"
        echo "Por favor, inicia Docker y vuelve a intentar."
        exit 1
    fi
}

# Función para verificar si Docker Compose está disponible
check_docker_compose() {
    if ! command -v docker compose > /dev/null 2>&1; then
        echo -e "${RED}Error: Docker Compose no está instalado${NC}"
        echo "Por favor, instala Docker Compose y vuelve a intentar."
        exit 1
    fi
}

# Función para crear directorios de datos si no existen
create_data_dirs() {
    mkdir -p data/ollama data/open-webui
}

# Función para iniciar servicios
start_service() {
    local option=$1
    
    # Crear directorios de datos
    create_data_dirs
    
    case $option in
        "webui")
            echo -e "${GREEN}Iniciando Ollama + Open WebUI...${NC}"
            docker compose --profile webui up -d
            echo -e "${GREEN}Servicios iniciados:${NC}"
            echo -e "  🤖 Ollama: http://localhost:11434"
            echo -e "  🌐 Open WebUI: http://localhost:8080"
            ;;
        ""|"ollama")
            echo -e "${GREEN}Iniciando Ollama...${NC}"
            docker compose up -d ollama
            echo -e "${GREEN}Ollama iniciado en http://localhost:11434${NC}"
            ;;
        *)
            echo -e "${RED}Error: Opción inválida '$option'${NC}"
            echo "Opciones válidas: ollama, webui"
            exit 1
            ;;
    esac
}

# Función para detener servicios
stop_service() {
    echo -e "${YELLOW}Deteniendo todos los servicios de Ollama...${NC}"
    docker compose down
    echo -e "${GREEN}Servicios detenidos${NC}"
}

# Función para reiniciar servicios
restart_service() {
    local option=$1
    
    echo -e "${YELLOW}Reiniciando servicios...${NC}"
    stop_service
    sleep 2
    start_service $option
}

# Función para mostrar logs
show_logs() {
    local service=$1
    
    case $service in
        "webui")
            docker compose logs -f open-webui
            ;;
        "ollama"|"")
            docker compose logs -f ollama
            ;;
        *)
            echo -e "${RED}Error: Opción inválida '$service'${NC}"
            echo "Opciones válidas: ollama, webui"
            exit 1
            ;;
    esac
}

# Función para mostrar estado
show_status() {
    echo -e "${BLUE}Estado de los contenedores Ollama:${NC}"
    echo ""
    docker compose ps
    echo ""
    echo -e "${BLUE}Uso de recursos:${NC}"
    docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}" 2>/dev/null || echo "No se pudo obtener estadísticas de recursos"
}

# Función para listar modelos
list_models() {
    echo -e "${BLUE}Modelos disponibles en Ollama:${NC}"
    echo ""
    if docker compose ps ollama | grep -q "Up"; then
        docker exec ollama ollama list
    else
        echo -e "${YELLOW}Ollama no está ejecutándose. Ejecuta '$0 start' para iniciarlo.${NC}"
    fi
}

# Función para descargar modelo
pull_model() {
    local model=$1
    
    if [ -z "$model" ]; then
        echo -e "${RED}Error: Debes especificar un modelo${NC}"
        echo "Ejemplos:"
        echo "  $0 pull opencoder:1.5b"
        echo "  $0 pull deepseek-coder:6.7b"
        echo "  $0 pull alientelligence/genaiimagecsprompt"
        exit 1
    fi
    
    echo -e "${GREEN}Descargando modelo $model...${NC}"
    docker exec ollama ollama pull $model
    echo -e "${GREEN}Modelo $model descargado exitosamente${NC}"
}

# Función para probar la API
test_api() {
    echo -e "${BLUE}Probando API de Ollama en http://localhost:11434...${NC}"
    echo ""
    
    # Verificar si el servicio está ejecutándose
    if ! curl -s http://localhost:11434/api/version > /dev/null; then
        echo -e "${RED}Error: Ollama no está ejecutándose en http://localhost:11434${NC}"
        echo "Ejecuta '$0 start' para iniciar Ollama"
        exit 1
    fi
    
    # Verificar versión
    echo -e "${BLUE}Versión de Ollama:${NC}"
    curl -s http://localhost:11434/api/version | jq -r '.version' 2>/dev/null || curl -s http://localhost:11434/api/version
    
    echo ""
    echo -e "${BLUE}Modelos disponibles:${NC}"
    curl -s http://localhost:11434/api/tags | jq -r '.models[].name' 2>/dev/null || curl -s http://localhost:11434/api/tags
    
    echo ""
    echo -e "${YELLOW}Para descargar modelos:${NC}"
    echo "  $0 pull opencoder:1.5b"
    echo "  $0 pull deepseek-coder:6.7b"
    echo "  $0 pull deepseek-r1"
    echo "  $0 pull deepseek-r1:1.5b"
    echo "  $0 pull alientelligence/genaiimagecsprompt"
}

# Función para limpiar
clean_all() {
    echo -e "${YELLOW}⚠️  ADVERTENCIA: Esto eliminará todos los datos de Ollama${NC}"
    read -p "¿Estás seguro? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}Limpiando contenedores y datos...${NC}"
        docker compose down -v
        rm -rf data/
        echo -e "${GREEN}Limpieza completada${NC}"
    else
        echo -e "${BLUE}Limpieza cancelada${NC}"
    fi
}

# Función principal
main() {
    local command=$1
    local option=$2
    
    # Verificar dependencias
    check_docker
    check_docker_compose
    
    case $command in
        "start")
            start_service $option
            ;;
        "stop")
            stop_service
            ;;
        "restart")
            restart_service $option
            ;;
        "logs")
            show_logs $option
            ;;
        "status")
            show_status
            ;;
        "pull")
            pull_model $option
            ;;
        "list")
            list_models
            ;;
        "test")
            test_api
            ;;
        "clean")
            clean_all
            ;;
        "help"|"-h"|"--help"|"")
            show_help
            ;;
        *)
            echo -e "${RED}Error: Comando desconocido '$command'${NC}"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# Ejecutar función principal con argumentos
main "$@" 