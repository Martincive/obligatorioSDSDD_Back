# Obligatorio Sistemas de Soporte – Chatbot RAG con FastAPI + Ollama + Chroma

Este proyecto implementa un chatbot de análisis de ventas utilizando técnicas de RAG (Retrieval Augmented Generation). El bot responde preguntas sobre productos, clientes, categorías, ventas mensuales y más, a partir del archivo Excel provisto para el obligatorio.

## Requerimientos

- Python 3.10+
- Ollama corriendo en el puerto 11434 (en mi caso, esta corriendo en un container de docker)
- uv instalado globalmente
- Archivo Excel en: data/TrabajoFinalPowerBI(1).xlsx
- Archivo requirements.txt incluido en el repositorio

## Instalación del entorno con venv + uv

Crear el entorno virtual:
```
uv venv .venv
```
Activar entorno:
Windows:
```
.venv\Scripts\activate
```
Linux/macOS:
```
source .venv/bin/activate
```
Instalar dependencias:
```
uv pip install -r requirements.txt
```

## Verificar que Ollama está activo:
```
curl http://localhost:11434/api/tags
```
Modelos necesarios:
```
ollama pull llama3.2:3b
ollama pull snowflake-arctic-embed
```

## Ejecutar FastAPI
```
uvicorn app:app --port 8000 --reload
```
Verificar:
```
curl http://localhost:8000/health
```
## Endpoints

Chat con streaming SSE:
curl -N -X POST http://localhost:8000/chat/stream -H "Content-Type: application/json" -d "{\"question\":\"Qué productos vendieron en total?\"}"

## Estructura del proyecto
```
obligatorioSDSDD_Back/
├── app.py
├── rag_pipeline.py
├── data_loader.py
├── settings.py
├── requirements.txt
├── .env
├── data/
│ └── TrabajoFinalPowerBI(1).xlsx
└── chroma_db/
```
## Notas importantes

El vector store se guarda en chroma_db/.  
Si cambiás la lógica de documentos, embeddings o intents, borrar la carpeta:
```
rm -rf chroma_db
```
El sistema volverá a generarla automáticamente al iniciar.
