import os
from dotenv import load_dotenv

load_dotenv()

MODEL_LLM = os.getenv("MODEL_LLM", "llama3.2:3b")
MODEL_EMBEDDINGS = os.getenv("MODEL_EMBEDDINGS", "snowflake-arctic-embed")
DATA_FILE = os.getenv("DATA_FILE", "data/TrabajoFinalPowerBI(1).xlsx")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
