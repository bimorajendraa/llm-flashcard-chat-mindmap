from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openrouter import call_openrouter
from retriever import search_scholarships, detect_intent, extract_level, extract_type, extract_index

app = FastAPI(title="OpenRouter Learning AI")
LAST_CONTEXT = {}

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
    session_id = "local_user"
    user_msg_raw = data.text.strip()

    if not user_msg_raw:
        return {"result": "Silakan ketik pertanyaan terkait beasiswa 😊"}

    user_msg = user_msg_raw.lower()
    intent = detect_intent(user_msg)

    # =========================
    # INIT SESSION
    # =========================
    if session_id not in LAST_CONTEXT:
        LAST_CONTEXT[session_id] = {"items": []}

    ctx = LAST_CONTEXT[session_id]

    # =========================
    # 1. SMALL TALK
    # =========================
    if intent == "small_talk":
        return {
            "result": (
                "Halo 👋 Aku bisa bantu kamu mencari informasi beasiswa.\n\n"
                "Contoh pertanyaan:\n"
                "- ada beasiswa apa saja?\n"
                "- beasiswa S2 gratis\n"
                "- list beasiswa\n"
            )
        }

    # =========================
    # 2. AMBIL DATA (DEFAULT)
    # =========================
    # Kalau user nanya apa pun yang berkaitan beasiswa
    items, _ = search_scholarships(user_msg, limit=5)

    # Fallback: kalau kosong, coba ambil umum
    if not items:
        items, _ = search_scholarships("beasiswa", limit=5)

    if not items:
        return {
            "result": "Saat ini belum ada data beasiswa di database kami."
        }

    ctx["items"] = items

    # =========================
    # 3. FILTER LEVEL
    # =========================
    level = extract_level(user_msg)
    if level:
        filtered = [s for s in ctx["items"] if s["level"] == level]
        if filtered:
            ctx["items"] = filtered
        else:
            return {
                "result": f"Saat ini belum ada beasiswa jenjang {level} di database kami."
            }

    # =========================
    # 4. FILTER TYPE (GRATIS)
    # =========================
    ftype = extract_type(user_msg)
    if ftype:
        filtered = [s for s in ctx["items"] if s["type"] == ftype]
        if filtered:
            ctx["items"] = filtered
        else:
            return {
                "result": "Belum ada beasiswa gratis (full funded) dari daftar tersebut."
            }

    # =========================
    # 5. AMBIL LINK NOMOR
    # =========================
    idx = extract_index(user_msg)
    if idx is not None:
        if idx < 0 or idx >= len(ctx["items"]):
            return {"result": "Nomor beasiswa tidak valid."}

        s = ctx["items"][idx]
        return {
            "result": (
                f"Link pendaftaran {s['scholarship_name']}:\n"
                f"{s['application_link']}"
            )
        }

    # =========================
    # 6. TAMPILKAN LIST
    # =========================
    response = "Berikut beberapa beasiswa yang bisa kamu pertimbangkan:\n\n"

    for i, s in enumerate(ctx["items"], start=1):
        response += (
            f"{i}. {s['scholarship_name']} ({s['country']})\n"
            f"   Jenjang: {s['level']} | Pendanaan: {s['type']}\n"
            f"   Pendaftaran: {s['open_date']} sampai {s['closed_date']}\n\n"
        )

    response += (
        "Kamu bisa lanjut dengan:\n"
        "- 'link nomor 1'\n"
        "- 'yang gratis'\n"
        "- 'yang S2'\n"
    )

    return {"result": response}

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
