const API = "http://127.0.0.1:8000";
function addChat(role, text) {
  const box = document.getElementById("chatBox");
  const bubble = document.createElement("div");

  bubble.className =
    role === "user"
      ? "self-end bg-blue-600 text-white px-3 py-2 rounded-lg max-w-xs"
      : "self-start bg-white border px-3 py-2 rounded-lg max-w-xs";

  bubble.innerText = text;
  box.appendChild(bubble);
  box.scrollTop = box.scrollHeight;
}

async function sendChat() {
  const input = document.getElementById("chatInput");
  const text = input.value.trim();
  if (!text) return;

  addChat("user", text);
  input.value = "";

  const res = await fetch(`${API}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text }),
  });

  const data = await res.json();
  addChat("ai", data.result);
}

// ================= FLASHCARD =================
async function generateFlashcard() {
  const text = document.getElementById("flashcardInput").value;
  const output = document.getElementById("flashcardOutput");
  output.innerHTML = "⏳ Loading...";

  const res = await fetch(`${API}/flashcard`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text }),
  });

  const data = await res.json();
  output.innerHTML = "";

  try {
    const cards = JSON.parse(data.result);
    cards.forEach((card) => {
      const div = document.createElement("div");
      div.className = "border rounded-lg p-3 bg-slate-50";
      div.innerHTML = `
        <p class="font-semibold">Q: ${card.question}</p>
        <p class="mt-1 text-slate-700">A: ${card.answer}</p>
      `;
      output.appendChild(div);
    });
  } catch {
    output.innerText = data.result;
  }
}

// ================= MIND MAP =================
async function generateMindmap() {
  const text = document.getElementById("mindmapInput").value;
  const output = document.getElementById("mindmapOutput");
  output.innerText = "⏳ Loading...";

  const res = await fetch(`${API}/mindmap`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text }),
  });

  const data = await res.json();
  output.innerText = data.result;
}
