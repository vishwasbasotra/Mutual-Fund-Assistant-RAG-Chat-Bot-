import os
from dotenv import load_dotenv

# Load environment variables from .env file at the project root
config_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(config_dir, ".."))
env_path = os.path.join(project_root, ".env")

if os.path.exists(env_path):
    load_dotenv(dotenv_path=env_path)
else:
    load_dotenv()

CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", os.path.join(project_root, "chroma_db"))
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "mutual_fund_faq")
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "BAAI/bge-small-en-v1.5")

# Groq API Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")  # Fast and reliable active model
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

# Server Configuration
HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", "8000"))
