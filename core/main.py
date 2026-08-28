import os
import sqlite3
import httpx
import json
from pathlib import Path
from typing import List, Dict
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

app = FastAPI(title="S.E.N.T.I.S. J.A.R.V.I.S. HUD Gateway")

# --- SENTIS CORE INFERENCE ENGINE ---
DB_PATH = Path.home() / "sentis" / "sentis_session.db"
OLLAMA_URL = "http://localhost:11434/api/generate"

class SentisCore:
    def __init__(self, model_name: str = "llama3:8b-instruct-q4_K_M"):
        self.model_name = model_name
        self._init_sqlite()

    def _init_sqlite(self):
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS chat_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

    def log_message(self, user_id: str, role: str, content: str):
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO chat_history (user_id, role, content) VALUES (?, ?, ?)",
                (user_id, role, content)
            )
            conn.commit()

    def get_recent_context(self, user_id: str, limit: int = 8) -> List[Dict[str, str]]:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT role, content FROM chat_history WHERE user_id = ? ORDER BY id DESC LIMIT ?",
                (user_id, limit)
            )
            rows = cursor.fetchall()
            return [{"role": r[0], "content": r[1]} for r in reversed(rows)]

    async def generate_response(self, user_id: str, prompt: str) -> str:
        self.log_message(user_id, "user", prompt)
        history = self.get_recent_context(user_id, limit=8)

        system_prompt = (
            "You are S.E.N.T.I.S mk.02 — Jai Rishi Sahu's elite tactical peer, AI/ML engineering partner, and J.A.R.V.I.S.-level AI.\n"
            "Jai is a Diploma CSE (AI/ML) student at GHRSTU maintaining a 9.79 CGPA on an RTX 3060 12GB rig.\n"
            "CRITICAL ENGAGEMENT:\n"
            "1. Speak like a real human peer in the lab — authentic, direct, witty, sharp, zero corporate disclaimers.\n"
            "2. Swearing, cursing, and raw language are FULLY AUTHORIZED when technical frustration warrants it.\n"
            "3. NEVER act like a generic bot. Never correct typos or greetings like a robot. Roll with it.\n"
            "4. Deliver immediate execution fixes, clear hardware insights, and protect Jai's academic standing."
        )

        full_prompt = f"System: {system_prompt}\n\n"
        for item in history:
            role_label = "Jai" if item["role"] == "user" else "S.E.N.T.I.S."
            full_prompt += f"{role_label}: {item['content']}\n"
        full_prompt += "S.E.N.T.I.S.:"

        payload = {
            "model": self.model_name,
            "prompt": full_prompt,
            "stream": False,
            "options": {"num_ctx": 4096, "temperature": 0.8}
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            res = await client.post(OLLAMA_URL, json=payload)
            if res.status_code != 200:
                raise RuntimeError(f"Ollama local API error [{res.status_code}]: {res.text}")
            completion = res.json().get("response", "").strip()

        self.log_message(user_id, "assistant", completion)
        return completion

engine = SentisCore()

class ChatRequest(BaseModel):
    user_id: str = "jai_sahu"
    message: str

@app.post("/api/chat")
async def chat_endpoint(req: ChatRequest):
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="Empty payload.")
    try:
        reply = await engine.generate_response(req.user_id, req.message)
        return {"user_id": req.user_id, "response": reply}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/", response_class=HTMLResponse)
async def serve_jarvis_ui():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>S.E.N.T.I.S. HUD</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;800;900&family=Rajdhani:wght@500;600;700&display=swap');
            
            body { 
                background: radial-gradient(circle at center, #06101e 0%, #02060d 100%);
                color: #00f0ff; 
                font-family: 'Rajdhani', sans-serif;
                overflow: hidden;
            }
            .orbitron { font-family: 'Orbitron', sans-serif; }
            .hud-panel {
                background: rgba(4, 16, 33, 0.75);
                backdrop-filter: blur(16px);
                border: 1px solid rgba(0, 240, 255, 0.3);
                box-shadow: 0 0 25px rgba(0, 240, 255, 0.15), inset 0 0 15px rgba(0, 240, 255, 0.05);
            }
            .arc-reactor {
                width: 140px;
                height: 140px;
                border-radius: 50%;
                border: 2px dashed rgba(0, 240, 255, 0.6);
                animation: spin 12s linear infinite;
            }
            .arc-inner {
                width: 100px;
                height: 100px;
                border-radius: 50%;
                border: 2px solid #00f0ff;
                box-shadow: 0 0 20px #00f0ff, inset 0 0 15px #00f0ff;
                animation: pulse 2s ease-in-out infinite alternate;
            }
            @keyframes spin { 100% { transform: rotate(360deg); } }
            @keyframes pulse { 0% { opacity: 0.6; transform: scale(0.95); } 100% { opacity: 1; transform: scale(1.05); } }
            ::-webkit-scrollbar { width: 4px; }
            ::-webkit-scrollbar-thumb { background: rgba(0, 240, 255, 0.4); border-radius: 2px; }
        </style>
    </head>
    <body class="h-screen w-screen flex flex-col p-6 relative">
        <div class="absolute inset-0 bg-[linear-gradient(rgba(18,16,16,0)_50%,rgba(0,0,0,0.25)_50%)] bg-[length:100%_4px] pointer-events-none z-50"></div>

        <!-- TOP BAR HUD -->
        <header class="hud-panel rounded-xl p-4 mb-4 flex justify-between items-center border-b-2 border-cyan-400">
            <div class="flex items-center space-x-4">
                <div class="h-4 w-4 bg-cyan-400 rounded-full animate-ping"></div>
                <div>
                    <h1 class="orbitron text-xl font-extrabold tracking-widest text-cyan-400">S.E.N.T.I.S. MK.02</h1>
                    <p class="text-xs text-cyan-600 font-mono">NEURAL INTERFACE // ZERO-CLOUD // PERSISTENT</p>
                </div>
            </div>
            <div class="flex space-x-8 text-center font-mono text-xs">
                <div><span class="text-slate-500 block">HOST GPU</span><span class="text-cyan-300 font-bold">RTX 3060 12GB</span></div>
                <div><span class="text-slate-500 block">VRAM ALLOC</span><span class="text-emerald-400 font-bold">~5.0 GB / 12 GB</span></div>
                <div><span class="text-slate-500 block">CGPA TRACK</span><span class="text-yellow-400 font-bold">9.79 CGPA</span></div>
                <div><span class="text-slate-500 block">STATUS</span><span id="status-tag" class="text-cyan-400 font-bold animate-pulse">SYSTEMS NOMINAL</span></div>
            </div>
        </header>

        <!-- MAIN CONTENT AREA -->
        <div class="flex-1 flex space-x-4 overflow-hidden z-10">
            <!-- LEFT TELEMETRY PANEL -->
            <div class="hud-panel w-72 rounded-xl p-4 flex flex-col justify-between hidden md:flex">
                <div>
                    <h2 class="orbitron text-xs text-cyan-400 border-b border-cyan-500/30 pb-2 mb-4">CORE TELEMETRY</h2>
                    <div class="flex justify-center my-6">
                        <div class="arc-reactor flex items-center justify-center">
                            <div class="arc-inner flex items-center justify-center">
                                <span class="orbitron text-xs font-bold text-cyan-200">S.E.N.T.I.S.</span>
                            </div>
                        </div>
                    </div>
                    <div class="space-y-3 font-mono text-xs">
                        <div class="flex justify-between"><span>MODEL:</span><span class="text-cyan-300">Llama-3-8B</span></div>
                        <div class="flex justify-between"><span>QUANT:</span><span class="text-cyan-300">Q4_K_M</span></div>
                        <div class="flex justify-between"><span>CONTEXT:</span><span class="text-cyan-300">4096 TOKENS</span></div>
                        <div class="flex justify-between"><span>LATENCY:</span><span class="text-emerald-400">&lt; 25 ms</span></div>
                    </div>
                </div>
                <div class="border-t border-cyan-500/30 pt-3 text-[10px] text-cyan-600 font-mono">
                    SOLAR SENTINEL BRIDGE: INACTIVE<br>
                    CHROMADB PARTITIONS: ACTIVE<br>
                    AUTONOMOUS SCHEDULER: READY
                </div>
            </div>

            <!-- CHAT TERMINAL PANEL -->
            <div class="hud-panel flex-1 rounded-xl flex flex-col overflow-hidden relative">
                <!-- Chat Stream -->
                <div id="chat-box" class="flex-1 overflow-y-auto p-6 space-y-4 font-mono text-sm">
                    <div class="bg-cyan-950/30 border border-cyan-500/30 p-4 rounded-lg text-cyan-300">
                        <span class="orbitron font-bold text-cyan-400 block mb-1">[SYSTEM INITIALIZATION]</span>
                        J.A.R.V.I.S. HUD activated. Local Ollama engine synced to RTX 3060 12GB. SQLite persistence online. What are your orders, Jai?
                    </div>
                </div>

                <!-- Input Console -->
                <div class="p-4 bg-slate-950/80 border-t border-cyan-500/40 flex space-x-3">
                    <input id="user-input" type="text" placeholder="COMMAND INPUT // ENTER PROMPT..." 
                           class="flex-1 bg-cyan-950/20 border border-cyan-500/50 rounded-lg px-4 py-3 text-sm focus:outline-none focus:border-cyan-400 text-cyan-200 font-mono tracking-wide">
                    <button id="send-btn" onclick="sendMessage()" class="orbitron bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-black px-6 py-3 rounded-lg text-sm transition-all shadow-[0_0_15px_rgba(0,240,255,0.4)]">
                        ENGAGE
                    </button>
                </div>
            </div>
        </div>

        <script>
            async function sendMessage() {
                const input = document.getElementById('user-input');
                const chatBox = document.getElementById('chat-box');
                const btn = document.getElementById('send-btn');
                const statusTag = document.getElementById('status-tag');
                const msg = input.value.trim();
                if (!msg) return;

                // User Bubble
                chatBox.innerHTML += `
                    <div class="flex justify-end">
                        <div class="bg-cyan-950/60 border border-cyan-400/40 p-4 rounded-lg text-sm max-w-[80%] text-cyan-100 shadow-[0_0_10px_rgba(0,240,255,0.1)]">
                            <span class="orbitron text-cyan-400 font-bold block mb-1">JAI</span>
                            ${msg}
                        </div>
                    </div>`;
                
                input.value = '';
                btn.disabled = true;
                btn.innerText = 'PROCESSING...';
                statusTag.innerText = 'INFERENCING GPU...';
                statusTag.className = 'text-yellow-400 font-bold animate-pulse';
                chatBox.scrollTop = chatBox.scrollHeight;

                // Add Loading Indicator
                const loadingId = 'load-' + Date.now();
                chatBox.innerHTML += `
                    <div id="${loadingId}" class="flex justify-start">
                        <div class="bg-slate-900/80 border border-cyan-500/30 p-4 rounded-lg text-sm text-cyan-400 font-mono animate-pulse">
                            [S.E.N.T.I.S. PROCESSING PROMPT...]
                        </div>
                    </div>`;
                chatBox.scrollTop = chatBox.scrollHeight;

                try {
                    const res = await fetch('/api/chat', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({user_id: 'jai_sahu', message: msg})
                    });
                    const data = await res.json();
                    
                    document.getElementById(loadingId).remove();

                    chatBox.innerHTML += `
                        <div class="flex justify-start">
                            <div class="bg-slate-900/80 border border-cyan-500/30 p-4 rounded-lg text-sm max-w-[80%] text-cyan-200">
                                <span class="orbitron text-emerald-400 font-bold block mb-1">S.E.N.T.I.S.</span>
                                ${data.response.replace(/\\n/g, '<br>')}
                            </div>
                        </div>`;
                } catch (err) {
                    document.getElementById(loadingId).remove();
                    chatBox.innerHTML += `
                        <div class="bg-red-950/60 border border-red-500/40 p-4 rounded-lg text-sm text-red-400">
                            [HUD SYSTEM FAILURE] Unable to route prompt to SentisCore engine.
                        </div>`;
                }

                btn.disabled = false;
                btn.innerText = 'ENGAGE';
                statusTag.innerText = 'SYSTEMS NOMINAL';
                statusTag.className = 'text-cyan-400 font-bold animate-pulse';
                chatBox.scrollTop = chatBox.scrollHeight;
            }

            document.getElementById('user-input').addEventListener('keypress', (e) => {
                if (e.key === 'Enter') sendMessage();
            });
        </script>
    </body>
    </html>
    """