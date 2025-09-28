import os
from pathlib import Path

ASSISTANT_NAME = "jarvis"

def _load_env_fallback():
    """
    Lightweight .env loader to help Windows/PowerShell cases where users ran `set`
    which doesn't populate process env for Python. We try these locations:
      - ./envJarvis/.env
      - ./.env
      - ./envJarvis/HF_API_TOKEN.txt (token only)
    """
    root = Path(__file__).resolve().parents[1]
    candidates = [root / "envJarvis" / ".env", root / ".env"]
    for f in candidates:
        if f.exists():
            try:
                for line in f.read_text(encoding="utf-8").splitlines():
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    k, v = line.split("=", 1)
                    k = k.strip()
                    v = v.strip().strip('"').strip("'")
                    if k and v and k not in os.environ:
                        os.environ[k] = v
            except Exception:
                pass
    # Single-file token fallback
    token_file = root / "envJarvis" / "HF_API_TOKEN.txt"
    if token_file.exists() and "HF_API_TOKEN" not in os.environ:
        try:
            os.environ["HF_API_TOKEN"] = token_file.read_text(encoding="utf-8").strip()
        except Exception:
            pass

# Try to ensure environment is loaded before reading
_load_env_fallback()

# Hugging Face Inference API configuration
HF_API_TOKEN = os.getenv("HF_API_TOKEN")  # set environment variable or use .env/txt fallback
HF_MODEL = os.getenv("HF_MODEL", "meta-llama/Meta-Llama-3.1-8B-Instruct")