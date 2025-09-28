import os

ASSISTANT_NAME = "jarvis"

# Hugging Face Inference API configuration
HF_API_TOKEN = os.getenv("HF_API_TOKEN")  # set environment variable or fill directly
HF_MODEL = os.getenv("HF_MODEL", "meta-llama/Meta-Llama-3.1-8B-Instruct")