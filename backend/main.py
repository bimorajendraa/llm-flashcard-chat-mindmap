from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openrouter import call_openrouter

app = FastAPI(title="OpenRouter Learning AI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class TextInput(BaseModel):
    text: str

@app.get("/")
def root():
    return {
        "status": "OK",
        "message": "OpenRouter AI Backend Running",
        "endpoints": ["/chat", "/flashcard", "/mindmap"]
    }

# ================= CHATBOT =================
@app.post("/chat")
def chat(data: TextInput):
    prompt = f"""
Jawab sebagai tutor pembelajaran.
Jawaban singkat, jelas, maksimal 5 kalimat.

Pertanyaan:
{data.text}
"""
    return {"result": call_openrouter(prompt)}

# ================= FLASHCARD =================
@app.post("/flashcard")
def flashcard(data: TextInput):
    prompt = f"""
Buatkan flashcard dari materi berikut.

Aturan:
- Format JSON
- Pertanyaan singkat
- Jawaban maksimal 2 kalimat

Format:
[
  {{
    "question": "...",
    "answer": "..."
  }}
]

Materi:
{data.text}
"""
    return {"result": call_openrouter(prompt)}

# ================= MIND MAP =================
@app.post("/mindmap")
def mindmap(data: TextInput):
    prompt = f"""
Buatkan mind map dalam format JSON hierarki.

Format:
{{
  "root": "...",
  "children": [
    {{
      "title": "...",
      "children": []
    }}
  ]
}}

Teks:
{data.text}
"""
    return {"result": call_openrouter(prompt)}
