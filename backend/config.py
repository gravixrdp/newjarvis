import os
from pathlib import Path

ASSISTANT_NAME = "jarvis"

def _load_env_fallback():
    """
    Lightweight .env loader for Windows/PowerShell cases.
    Tries:
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
HF_API_TOKEN = os.getenv("HF_API_TOKEN")  # set env, or provide via .env/txt fallback
# Correct public model id (accept terms on HF first): meta-llama/Llama-3.1-8B-Instruct
HF_MODEL = os.getenv("HF_MODEL", "meta-llama/Llama-3.1-8B-Instruct")

# Optional mic device index for SpeechRecognition (see sr.Microphone.list_microphone_names())
MIC_DEVICE_INDEX = None
try:
    _idx = os.getenv("MIC_DEVICE_INDEX")
    if _idx is not None and _idx != "":
        MIC_DEVICE_INDEX = int(_idx)
except Exception:
    MIC_DEVICE_INDEX = None