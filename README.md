```markdown
# S.E.N.T.I.S. (Synthetic Entity for Neural Task Integration & Scheduling)

> **Local-First, No-Restriction, Multi-Tenant AI Assistant Ecosystem**  
> **Hardware Hub:** RTX 3060 12GB (or any other better or equivalent gpu) VRAM | Windows 11 + WSL2 (Ubuntu 22.04)[cite: 2]  

---

## 🚀 Executive Overview

**S.E.N.T.I.S.** is a privacy-hardened, zero-cloud AI assistant ecosystem designed to run entirely offline on consumer hardware. Powered by a 12+GB VRAM advantage, it hosts 13B parameter LLMs locally via Ollama and llama.cpp inside WSL2, completely eliminating external API latency, subscription fees, and data leakage.

---

## 🛠️ System Architecture & Stack

```text
[Windows 11 Host] <---> [WSL2 Ubuntu 22.04 AI Workbench]
                             ├──> Ollama Local REST API (:11434) [RTX 3060 12GB]
                             ├──> FastAPI S.E.N.T.I.S HUD Gateway (:8000)
                             ├──> SQLite Session Persistence & ChromaDB Partitions
                             └──> Automated Git Pre-Commit Hook & Documentation Engine

```

* **Host OS:** Windows 11 (handling native gaming, drivers, and hardware passthrough)


* **AI Workbench:** WSL2 Ubuntu 22.04 LTS (running Python 3.10, FastAPI, and local inference)


* **Inference Engine:** Ollama + `llama3:8b-instruct-q4_K_M` (running natively in GPU memory)


* **Interface:** Custom neon cyan S.E.N.T.I.S Arc Reactor HUD with real-time hardware telemetry and typing feedback


* **Data Persistence:** Local SQLite database (`sentis_session.db`) and isolated ChromaDB vector collections



---

## 📂 Repository Structure

```text
.
├── core/
│   ├── engine.py       # Core orchestration wrapper and SQLite persistence manager
│   └── main.py         # FastAPI server and S.E.N.T.I.S HUD interface frontend
├── .git/
│   └── hooks/
│       └── pre-commit  # Automated STRUCTURE.md generation hook
├── sentis_session.db   # Local conversational history log
└── STRUCTURE.md        # Automatically updated project layout audit

```

---

## 💡 Key Features

1. **Zero-Cloud Sovereignty:** 100% local execution. Conversations, memory vectors, and personal documents never leave your machine.


2. **12GB VRAM Optimization:** Leverages the RTX 3060 12GB buffer to host models locally with massive headroom for embeddings and multi-tenant isolation.


3. **S.E.N.T.I.S HUD Interface:** Fast, responsive, glassmorphic terminal interface featuring real-time GPU telemetry and status monitoring.


4. **Automated Documentation:** Built-in Git pre-commit hook that dynamically updates and commits `STRUCTURE.md` on every change.



---

## ⚙️ Quick Start

1. **Ensure WSL2 & CUDA Drivers are Active:**
```bash
nvidia-smi

```


2. **Start the Ollama Daemon in WSL2:**
```bash
nohup ollama serve > ~/ollama.log 2>&1 &

```


3. **Launch the FastAPI S.E.N.T.I.S Gateway:**
```bash
cd ~/sentis
source venv/bin/activate
uvicorn core.main:app --host 0.0.0.0 --port 8000 --reload

```


4. **Access the HUD:** Open your browser on Windows and navigate to `http://localhost:8000`.

''markdown

      **thank you for reading please star this and use it!!**
---

## 📜 License & Security

Developed under strict local-first privacy guidelines. NO rights reserved by Jai Sahu.
