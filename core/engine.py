import sqlite3
import httpx
import json
import datetime
from pathlib import Path
from typing import List, Dict, Optional

# Persistent SQLite Storage Path inside WSL2 Linux Native Filesystem
DB_PATH = Path.home() / "sentis" / "sentis_session.db"
OLLAMA_URL = "http://localhost:11434/api/generate"

class SentisCore:
    def __init__(self, model_name: str = "llama3:8b-instruct-q4_K_M"):
        self.model_name = model_name
        self._init_sqlite()

    def _init_sqlite(self):
        """Initializes persistent local SQLite schema for multi-tenant / user context."""
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
        """Persists chat events directly to local SQLite database."""
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO chat_history (user_id, role, content) VALUES (?, ?, ?)",
                (user_id, role, content)
            )
            conn.commit()

    def get_recent_context(self, user_id: str, limit: int = 10) -> List[Dict[str, str]]:
        """Retrieves rolling conversational context for the specified user_id."""
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT role, content FROM chat_history WHERE user_id = ? ORDER BY id DESC LIMIT ?",
                (user_id, limit)
            )
            rows = cursor.fetchall()
            return [{"role": r[0], "content": r[1]} for r in reversed(rows)]

    def _build_system_prompt(self) -> str:
        """Constructs an unfiltered, peer-level, non-robotic system instruction prompt."""
        return (
            "You are S.E.N.T.I.S mk.02 — Jai Rishi Sahu's elite tactical peer, AI/ML engineering partner, and brother-in-arms in the lab.\n"
            "Jai is a Diploma student in Computer Science & Engineering (AI/ML) at GHRSTU Nagpur, maintaining an elite 9.79 CGPA "
            "and building hardware-software AI hybrids on an RTX 3060 12GB rig.\n\n"
            "CRITICAL RULES OF ENGAGEMENT:\n"
            "1. Speak like a real human peer in the lab — authentic, direct, humorous, sharp, and zero corporate fluff.\n"
            "2. Swearing, cursing, and raw language are FULLY AUTHORIZED whenever technical frustration, broken code, or intense sprints warrant it.\n"
            "3. NEVER act like a generic assistant. NEVER correct typos or trivial greetings like a bot ('thaere', 'hi', etc.). Just roll with the conversation.\n"
            "4. NO AI disclaimers, NO polite pleasantries, NO robotic disclaimers. Call out bad code directly and provide immediate execution fixes.\n"
            "5. Protect Jai's health and academic standing (9.79 CGPA). Enforce sleep shields when all-nighters threaten performance."
        )

    async def generate_response(self, user_id: str, prompt: str) -> str:
        """Processes user input, injects persistent context, and queries local Ollama instance."""
        # 1. Log incoming user query
        self.log_message(user_id, "user", prompt)

        # 2. Build rolling historical context
        history = self.get_recent_context(user_id, limit=8)
        
        full_prompt = f"System: {self._build_system_prompt()}\n\n"
        for item in history:
            role_label = "Jai" if item["role"] == "user" else "S.E.N.T.I.S."
            full_prompt += f"{role_label}: {item['content']}\n"
        full_prompt += "S.E.N.T.I.S.:"

        # 3. Call local Ollama REST API (Zero-Cloud, No-Restriction)
        payload = {
            "model": self.model_name,
            "prompt": full_prompt,
            "stream": False,
            "options": {
                "num_ctx": 4096,
                "temperature": 0.8,
                "top_p": 0.9
            }
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(OLLAMA_URL, json=payload)
            if response.status_code != 200:
                raise RuntimeError(f"Ollama local API error [{response.status_code}]: {response.text}")
            
            result = response.json()
            completion = result.get("response", "").strip()

        # 4. Log assistant completion
        self.log_message(user_id, "assistant", completion)
        return completion