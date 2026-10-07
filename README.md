# 📋 AI Requirement Analyzer (ArchReq-AI)

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.128%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![Groq](https://img.shields.io/badge/LLM-Groq%20(Llama--3.3--70B)-orange.svg)](https://groq.com/)
[![FAISS](https://img.shields.io/badge/Vector%20Store-FAISS-green.svg)](https://github.com/facebookresearch/faiss)
[![License](https://img.shields.io/badge/License-MIT-purple.svg)](LICENSE)

An enterprise-ready, AI-powered consulting engine that ingests unstructured, messy client requirement briefs (PDF/TXT) and transforms them into **structured specifications**, **gap & risk assessments**, **interactive semantic Q&A (RAG)**, and **branded, stakeholder-ready PDF reports**.

---

## 🚀 Key Features

* **🧠 Multi-Stage Consulting Reasoning Framework:**
  Guides LLMs through a structured 7-stage chain-of-thought analysis:
  1. *Requirement Clarification* (ambiguous phrases & implicit assumptions)
  2. *Intent Inference* (primary and secondary project objectives)
  3. *Decomposition* (functional vs. non-functional requirements & constraints)
  4. *Gap Identification* (identifying critical unstated details)
  5. *Severity Classification* (Critical / Moderate / Minor impact levels)
  6. *Risk Matrix Formulation* (category, impact, probability, and justifications)
  7. *Consolidated JSON Consolidation* (strict schema enforcement with self-healing retry logic)

* **🏢 Dual Domain Specialization:**
  * **Architectural Planning:** Spatial planning, zoning, structural considerations, and material choices.
  * **Software Architecture:** Architecture patterns, integration complexity, data management, and scalability.

* **🔍 Retrieval-Augmented Generation (RAG) Q&A:**
  * Text chunking with configurable overlap.
  * Local semantic embeddings via `sentence-transformers/all-MiniLM-L6-v2`.
  * Disk-persisted vector indexing using **FAISS** (`IndexFlatL2`).
  * Instant, hallucination-free document Q&A strictly grounded in document context.

* **⚡ Blazing Fast LLM Inference (Groq Powered):**
  * Powered by **Groq** (`llama-3.3-70b-versatile`) with automatic fallback to local OpenAI-compatible engines (LM Studio / Ollama).

* **📑 Automated Stakeholder PDF Generation:**
  * Builds multi-page branded PDF reports featuring Cover Page, Executive Summary, Requirement Breakdown, Missing Information lists, dynamic Risk Matrix tables, and Refined Prose appendix.
  * Built-in unicode sanitization preventing encoding errors across diverse text outputs.

* **🔐 Security & Authentication:**
  * User registration and login with **bcrypt** password hashing.
  * **JWT (JSON Web Token)** bearer authentication and user-isolated document access.

* **🗄️ Flexible Data Persistence:**
  * Powered by **SQLAlchemy** ORM.
  * Supports Cloud PostgreSQL (Neon, Supabase, AWS RDS) and zero-config local SQLite (`app.db`).

---

## 🏗️ Architecture & Workflow

```mermaid
flowchart TD
    User([User / Client]) -->|1. Sign Up / Login| Auth[JWT Auth API]
    User -->|2. Upload PDF or TXT| DocAPI[Document API]
    
    DocAPI -->|Extract & Normalize| TextUtil[Text & PDF Utilities]
    DocAPI -->|Save Record| DB[(PostgreSQL / SQLite)]
    
    DocAPI -->|Background Worker| Worker[Async Background Task]
    Worker -->|Split Text| Chunker[Chunking Engine]
    Worker -->|Embeddings| ST[SentenceTransformers all-MiniLM-L6-v2]
    ST -->|Persist Vectors| FAISS[(FAISS Vector Store)]
    Worker -->|Prompt Reasoning| LLM[Groq / Llama-3.3-70B]
    
    User -->|3. Query / Ask Questions| RAG[RAG Service]
    RAG -->|Similarity Search| FAISS
    RAG -->|Contextual Answer| LLM
    
    User -->|4. Download Report| PDF[PDF Generator FPDF]
    PDF -->|Download| ReportFile[requirements_id_premium.pdf]
```

---

## 📂 Project Structure

```text
Requirement_analyzer/
├── app/
│   ├── api/
│   │   ├── auth_routes.py        # User registration and JWT login endpoints
│   │   └── documents.py          # Upload, analyze, ask, and download routes
│   ├── services/
│   │   ├── ai_agent.py           # Master consulting prompts, Groq LLM integration
│   │   ├── background_task.py    # Asynchronous worker for chunking & embedding
│   │   ├── embedding_services.py # SentenceTransformer embedding logic
│   │   ├── pdf_generator.py      # Branded PDF generator with table layouts
│   │   ├── rag_services.py       # Vector retrieval + contextual question answering
│   │   ├── requirement_extractor.py # Legacy rule-based regex fallback
│   │   └── vector_store.py       # FAISS index persistence and similarity search
│   ├── utils/
│   │   ├── chunkers.py           # Text chunking with sliding window
│   │   ├── files.py              # File validation utilities
│   │   ├── pdf.py                # PDF extraction via pdfplumber
│   │   └── text.py               # Text normalization helpers
│   ├── auth.py                   # Password hashing (bcrypt) & JWT helpers
│   ├── database.py               # Database engine & session configuration
│   ├── main.py                   # FastAPI application entry point
│   ├── models.py                 # SQLAlchemy relational database models
│   └── schemas.py                # Pydantic request/response schemas
├── generate_docs/                # Directory for generated PDF deliverables
├── vector_db/                    # Disk persistence for FAISS indexes (.index, .pkl)
├── .env.example                  # Environment configuration template
├── requirements.txt              # Production Python dependencies
└── sample_input.txt              # Sample messy requirements document
```

---

## ⚙️ Installation & Setup

### 1. Prerequisites
* **Python 3.10+**
* A free [Groq API Key](https://console.groq.com/keys)

### 2. Clone and Setup Environment
```bash
# Clone the repository
git clone https://github.com/your-username/Requirement_analyzer.git
cd Requirement_analyzer/Requirement_analyzer-main

# Create and activate virtual environment
python -m venv venv

# On Windows (PowerShell):
.\venv\Scripts\Activate.ps1

# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file in the project root (you can copy from `.env.example`):
```env
# Groq API Configuration
GROQ_API_KEY=gsk_your_groq_api_key_here
LLM_MODEL=llama-3.3-70b-versatile

# Database Configuration
# Option A: Zero-config SQLite (Instant & Local)
DATABASE_URL=sqlite:///./app.db

# Option B: Cloud PostgreSQL (Neon / Supabase)
# DATABASE_URL=postgresql://user:password@ep-name.neon.tech/neondb?sslmode=require
```

### 5. Launch the Server
```bash
uvicorn app.main:app --reload
```
The server will start at **`http://127.0.0.1:8000`**.  
Interactive Swagger documentation is available at **`http://127.0.0.1:8000/docs`**.

---

## 🧪 API Usage Guide

### 1. User Registration & Authentication
* **`POST /auth/register`**: Creates a new user account.
  ```json
  {
    "email": "user@example.com",
    "password": "Password123!"
  }
  ```
* **`POST /auth/login`**: Authenticates user and returns a JWT token.
  ```json
  {
    "access_token": "eyJhbGciOi...",
    "token_type": "bearer"
  }
  ```
> *Click the green **Authorize** button in Swagger UI (`/docs`) and enter your token to test protected routes.*

### 2. Upload Document
* **`POST /documents/upload`**:
  * Form Data:
    * `file`: Upload `.txt` or `.pdf` (e.g. `sample_input.txt`)
    * `domain`: `architecture` or `software`
  * Triggers background text chunking, FAISS vector indexing, and initial extraction.

### 3. Analyze Requirements (LLM Multi-Stage Reasoning)
* **`POST /documents/{document_id}/analyze`**:
  * Runs the full 7-stage Groq LLM reasoning analysis.
  * Returns structured JSON breakdown (executive summary, functional/non-functional items, missing information, gap severity, and risk matrix).

### 4. Interactive Document Q&A (RAG)
* **`POST /documents/{document_id}/ask?question=...`**:
  * Retrieves relevant semantic chunks from FAISS and delivers a context-grounded response.
  * Example question: `"What are the requirements for parking and floors?"`

### 5. Download Branded PDF Report
* **`GET /documents/{document_id}/download`**:
  * Compiles and downloads an executive-styled PDF report with custom navy/gold styling, executive summaries, breakdown items, and dynamic risk matrix tables.

---

## 🛡️ Technologies Used

| Technology | Purpose |
| :--- | :--- |
| **FastAPI** | High-performance asynchronous REST API framework |
| **Groq API** | Ultra-fast LLM inference (`llama-3.3-70b-versatile`) |
| **Sentence-Transformers** | Local text embedding generation (`all-MiniLM-L6-v2`) |
| **FAISS** | Facebook AI Similarity Search for dense vector retrieval |
| **SQLAlchemy** | SQL Object-Relational Mapping (PostgreSQL & SQLite) |
| **FPDF / FPDF2** | Programmatic report and document PDF generation |
| **pdfplumber** | Accurate text extraction from uploaded PDF documents |
| **python-jose & passlib** | JWT authentication and bcrypt password hashing |

---

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
