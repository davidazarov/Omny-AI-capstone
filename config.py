# config.py
import os
from dotenv import load_dotenv
from pathlib import Path

# Load Environment Variables
base_dir = Path(__file__).parent
env_path = base_dir / ".env"
load_dotenv(dotenv_path=env_path)

# API Keys
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
LANGFUSE_PUBLIC_KEY = os.getenv("LANGFUSE_PUBLIC_KEY")
LANGFUSE_SECRET_KEY = os.getenv("LANGFUSE_SECRET_KEY")
LANGFUSE_HOST = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")

# Model Settings
MODEL_NAME = "gemini-2.5-pro"