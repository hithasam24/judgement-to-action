```markdown
# Judgment-to-Action AI System ⚖️

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-green)
![LangGraph](https://img.shields.io/badge/LangGraph-AI_Agents-orange)
![Qdrant](https://img.shields.io/badge/Qdrant-Vector_DB-red)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15.0%2B-blue)

An AI-driven pipeline designed to ingest unstructured, multi-page court judgment PDFs, extract key legal directives, and generate structured administrative action plans (Compliance, Appeal, No-Action). Built for government and enterprise legal departments, this system features a strict **Human-in-the-Loop (HITL)** verification layer to ensure 100% data reliability before reaching decision-makers.

## 🚀 Key Features

* **Layout-Aware PDF Parsing:** Utilizes **Docling** (and OpenCV) to parse multi-column legal documents, retaining structural metadata and spatial bounding boxes $(x_0, y_0, x_1, y_1)$ for visual source tracking.
* **Hybrid Semantic Search:** Uses **Qdrant** to store and query text chunks using both Dense Vectors (semantic meaning) and Sparse Vectors/BM25 (exact legal citations, case numbers).
* **Multi-Agent Orchestration:** Powered by **LangGraph**, breaking down extraction into deterministic states: Metadata Extraction, Directive Analysis, Action Plan Logic, and Grounding Verification.
* **Human-in-the-Loop (HITL) Verification:** Execution halts using PostgreSQL checkpointing. A human reviewer verifies extracted directives against visual bounding-box highlights on the original PDF before approving the data.
* **Trusted Dashboard:** Only records with a `VERIFIED` state are exposed to the production frontend, eliminating the risk of AI hallucination in legal administration.

## 🏗️ System Architecture

```text
+-------------------+       +-----------------------+       +-------------------------+
| Court PDF Upload  | ----> | Docling OCR & BBoxes  | ----> | Qdrant Hybrid Indexing  |
+-------------------+       +-----------------------+       +-------------------------+
                                                                        |
                                                                        v
+-------------------+       +-----------------------+       +-------------------------+
| PostgreSQL (DB)   | <---- | LangGraph State Graph | <---- |   LLM / Action Logic    |
| (Checkpoints)     |       | (Pause for Review)    |       | (Compliance vs Appeal)  |
+-------------------+       +-----------------------+       +-------------------------+
          |
          v
+-------------------+       +-----------------------+       +-------------------------+
|  HITL Dashboard   | ----> | Human Verification    | ----> | Trusted CCMS Dashboard  |
| (BBox Overlays)   |       | (Approve/Edit/Reject) |       | (VERIFIED records only) |
+-------------------+       +-----------------------+       +-------------------------+

```

## 🛠️ Tech Stack

* **Core & APIs:** Python, FastAPI, Pydantic
* **AI & Orchestration:** LangGraph, LangChain, HuggingFace Embeddings
* **Document Processing:** Docling, OpenCV
* **Databases:** PostgreSQL (State & Relational Data), Qdrant (Vector Database)

## ⚙️ Local Setup & Installation

### 1. Prerequisites

* Python 3.10+
* Docker & Docker Compose (for Qdrant & PostgreSQL)
* Git

### 2. Clone the Repository

```bash
git clone [https://github.com/yourusername/judgment-to-action-ai.git](https://github.com/yourusername/judgment-to-action-ai.git)
cd judgment-to-action-ai

```

### 3. Environment Variables

Create a `.env` file in the root directory:

```env
# Database configurations
DATABASE_URL=postgresql://user:password@localhost:5432/ccms_db
QDRANT_URL=http://localhost:6333

# API Keys
OPENAI_API_KEY=your_openai_api_key_here
# Or your preferred open-source LLM endpoint

```

### 4. Start External Services (Postgres & Qdrant)

```bash
docker-compose up -d

```

### 5. Install Dependencies

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

```

### 6. Run Database Migrations

```bash
alembic upgrade head

```

### 7. Start the FastAPI Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

```

## 📡 Core API Endpoints

| Method | Endpoint | Description |
| --- | --- | --- |
| `POST` | `/api/v1/documents/upload` | Ingests a PDF, runs Docling OCR, and starts LangGraph pipeline. |
| `GET` | `/api/v1/review/pending` | Fetches all judgments awaiting human verification. |
| `GET` | `/api/v1/review/{doc_id}` | Returns extracted directives with spatial bounding box coordinates. |
| `POST` | `/api/v1/review/{doc_id}/approve` | Commits human edits, updates state to `VERIFIED`, and resumes graph. |
| `GET` | `/api/v1/dashboard/verified` | Returns only verified action plans for the trusted frontend. |

## 📂 Project Structure

```text
├── app/
│   ├── api/            # FastAPI routes and endpoints
│   ├── core/           # Config, logging, and security
│   ├── db/             # PostgreSQL models and connection
│   ├── graph/          # LangGraph nodes, state schema, and workflow
│   ├── ingestion/      # Docling parsing and Qdrant chunking logic
│   └── schemas/        # Pydantic validation models
├── tests/              # Pytest unit and integration tests
├── docker-compose.yml  # Qdrant and Postgres containers
├── requirements.txt    # Python dependencies
└── README.md

```

## 🤝 Contributing

Contributions are welcome. Please ensure that any graph modifications include appropriate unit tests for state transitions and validation logic.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](https://www.google.com/search?q=LICENSE) file for details.

```

```
