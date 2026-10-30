import os
from dotenv import load_dotenv

# Load variables from .env
load_dotenv()


# ==============================
# Ollama Configuration
# ==============================

OLLAMA_URL = os.getenv(
    "OLLAMA_URL",
    "http://127.0.0.1:11434"
)

MODEL_NAME = os.getenv(
    "MODEL_NAME",
    "qwen3:8b"
)


# ==============================
# Notion Configuration
# ==============================

NOTION_TOKEN = os.getenv("NOTION_TOKEN")

NOTION_PARENT_PAGE_ID = os.getenv("NOTION_PARENT_PAGE_ID")


# ==============================
# Validate required settings
# ==============================

if not NOTION_TOKEN:
    raise ValueError(
        "NOTION_TOKEN is missing from the .env file"
    )

if not NOTION_PARENT_PAGE_ID:
    raise ValueError(
        "NOTION_PARENT_PAGE_ID is missing from the .env file"
    )