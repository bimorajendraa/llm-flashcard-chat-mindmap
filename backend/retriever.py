from db import get_db

GENERAL_KEYWORDS = [
    "beasiswa", "scholarship", "rekomendasi", "info", "daftar", "kuliah"
]

LEVEL_ALIASES = {
    "s1": "S1",
    "sarjana": "S1",
    "s2": "S2",
    "magister": "S2",
    "s3": "S3",
    "doktor": "S3",
}

TYPE_ALIASES = {
    "gratis": "full_funded",
    "full": "full_funded",
    "full funded": "full_funded",
    "fully funded": "full_funded",
    "half": "partial_funded",
    "setengah": "partial_funded",
    "partial": "partial_funded",
    "tuition": "tuition_only",
}

SMALL_TALK = [
    "halo", "hai", "hi", "pagi", "siang", "malam", "hello"
]

FOLLOW_UP_KEYWORDS = [
    "mana", "link", "tautan", "website", "daftar", "apply"
]

DATE_KEYWORDS = [
    "januari", "februari", "maret", "april",
    "mei", "juni", "juli", "agustus",
    "september", "oktober", "november", "desember"
]

def extract_level(message: str):
    msg = message.lower()
    for k, v in LEVEL_ALIASES.items():
        if k in msg:
            return v
    return None

def extract_type(message: str):
    msg = message.lower()
    for k, v in TYPE_ALIASES.items():
        if k in msg:
            return v
    return None

def extract_index(message: str):
    for i in range(1, 11):
        if str(i) in message:
            return i - 1
    return None

def detect_intent(message: str) -> str:
    msg = message.lower()

    if any(k in msg for k in SMALL_TALK):
        return "small_talk"

    if any(k in msg for k in FOLLOW_UP_KEYWORDS):
        return "follow_up"

    if any(k in msg for k in DATE_KEYWORDS):
        return "date_filter"

    if any(k in msg for k in GENERAL_KEYWORDS):
        return "general_scholarship"

    return "specific_scholarship"


def search_scholarships(message: str, limit: int = 5):
    conn = get_db()
    cur = conn.cursor(dictionary=True)

    intent = detect_intent(message)

    # ===============================
    # 1. GENERAL / BEASISWA UMUM
    # ===============================
    if intent == "general_scholarship":
        cur.execute("""
        SELECT scholarship_name, country, university, level, type,
               open_date, closed_date, application_link
        FROM scholarships
        WHERE status = 1 AND deleted_at IS NULL
        ORDER BY closed_date ASC
        LIMIT %s
        """, (limit,))
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return rows, intent

    # ===============================
    # 2. SPESIFIK (keyword)
    # ===============================
    kw = f"%{message}%"
    cur.execute("""
    SELECT scholarship_name, country, university, level, type,
           open_date, closed_date, application_link
    FROM scholarships
    WHERE status = 1
      AND deleted_at IS NULL
      AND (
        scholarship_name LIKE %s
        OR country LIKE %s
        OR university LIKE %s
        OR level LIKE %s
        OR type LIKE %s
      )
    ORDER BY closed_date ASC
    LIMIT %s
    """, (kw, kw, kw, kw, kw, limit))

    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows, intent
