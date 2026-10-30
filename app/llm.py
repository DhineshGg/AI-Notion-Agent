from langchain_ollama import ChatOllama

from config import (
    OLLAMA_URL,
    MODEL_NAME
)


# ==========================================
# Ollama LLM
# ==========================================

llm = ChatOllama(
    model=MODEL_NAME,
    base_url=OLLAMA_URL,
    temperature=0
)