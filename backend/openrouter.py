import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENROUTER_API_KEY")
BASE_URL = "https://openrouter.ai/api/v1/chat/completions"

if not API_KEY:
    raise RuntimeError("❌ OPENROUTER_API_KEY tidak ditemukan")

def call_openrouter(prompt: str) -> str:
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost",
        "X-Title": "Learning AI App"
    }

    payload = {
        # MODEL GRATIS & RINGAN
        "model": "mistralai/mistral-7b-instruct",
        "messages": [
            {"role": "system", "content": "Kamu adalah asisten pembelajaran."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.5,
        "max_tokens": 500
    }

    response = requests.post(BASE_URL, json=payload, headers=headers)

    try:
        data = response.json()
    except Exception:
        return "❌ Gagal membaca response OpenRouter"

    if response.status_code != 200:
        return f"❌ OpenRouter error {response.status_code}: {data}"

    return data["choices"][0]["message"]["content"]
