# NG12 Clinical Agent

A clinical decision support and conversational AI system built on NICE NG12 cancer referral guidelines.  
The system combines structured patient data with unstructured clinical guidance using a shared Retrieval-Augmented Generation (RAG) pipeline, grounded with explicit citations.

---

## 🔍 Project Overview

This project implements two tightly related capabilities:

1. **NG12 Cancer Risk Assessor**  
   Deterministic clinical decision support that evaluates whether a patient meets NICE NG12 criteria for urgent referral or investigation.

2. **Conversational NG12 RAG Agent**  
   A multi-turn chat interface that answers guideline questions using the same NG12 knowledge base, with strict grounding and citation requirements.

Both capabilities **reuse the same vector database, embeddings, and PDF ingestion outputs**, demonstrating a unified RAG architecture.

---


## 🧠 Architecture Summary

**Backend**
- FastAPI (Python)
- ChromaDB (local vector database)
- Google Vertex AI (Gemini 1.5 + embeddings)
- Modular agent and service layers

**Frontend**
- React + TypeScript (Vite)
- TailwindCSS
- Minimal clinical UI focused on clarity and explainability

**Data Sources**
- `patients.json` – simulated structured patient records
- NICE NG12 PDF – parsed, chunked, embedded once during ingestion

---

## 🧩 Core System Flow

1. User provides input (Patient ID or question)
2. Structured data is retrieved via a tool call (patients.json)
3. Relevant NG12 guideline chunks are retrieved from ChromaDB
4. The LLM synthesizes an answer using only retrieved evidence
5. Output includes:
   - Decision or answer
   - Reasoning
   - Explicit NG12 citations (page + chunk)

---

## 🩺 Part 1: NG12 Cancer Risk Assessor

### UI Inputs
- **Patient ID** – identifies a record in `patients.json`
- **Top-K** – number of guideline chunks retrieved
- **Assess** – triggers the assessment pipeline

### Backend Logic
- Fetch patient demographics and symptoms
- Retrieve relevant NG12 sections based on symptoms
- Apply guideline-driven reasoning
- Output a structured assessment

### Output
- Assessment classification (Urgent Referral / Investigation / Unclear)
- Short clinical reasoning
- Confidence score derived from retrieval quality
- Guideline citations (NG12 page + chunk ID)

---

## 💬 Part 2: Conversational NG12 RAG

### Chat Capabilities
- Multi-turn conversations using session IDs
- Follow-up questions grounded in prior context
- Strict citation enforcement
- Guardrails against unsupported medical advice

### Supported Endpoints
- `POST /chat`
- `GET /chat/{session_id}/history`
- `DELETE /chat/{session_id}`

### Failure Behavior
If insufficient evidence is found in NG12, the agent explicitly responds:
> “I couldn’t find support in the NG12 guideline for this.”

---

## 🎯 Key Design Principles

- **Single RAG Pipeline** reused across decision support and chat
- **No hallucinated thresholds or treatments**
- **Explainability-first UI** (citations + retrieval debug)
- **Clinical safety guardrails**
- **Production-style modular backend**

---

## ⚠️ Challenges Faced & Solutions

### 1. Grounding LLM Responses to Clinical Guidelines
**Challenge:**  
Preventing hallucinated medical thresholds or invented referral criteria.

**Solution:**  
- Retrieval-first reasoning
- Answer generation strictly limited to NG12 chunks
- Mandatory citation verification for every clinical statement

---

### 2. Reusing One RAG Pipeline Across Two Agents
**Challenge:**  
Supporting both deterministic decision support and conversational querying without duplicate ingestion or embeddings.

**Solution:**  
- Centralized PDF ingestion pipeline
- Shared ChromaDB vector store
- Same retriever reused by Assessor and Chat agents

---

### 3. Multi-Turn Context Without Losing Grounding
**Challenge:**  
Handling follow-ups (e.g., age thresholds) without drifting beyond NG12 evidence.

**Solution:**  
- Lightweight session memory
- Every response still requires fresh retrieval
- Context used only to refine queries, not invent answers

---

### 4. Safe Failure for Out-of-Scope Questions
**Challenge:**  
Users asking about treatments or prognosis not covered by NG12.

**Solution:**  
- Confidence-based guardrails
- Explicit refusal with explanation
- Zero speculative medical advice


---
## 🚀 Running the Project

### Backend
```bash
cd backend
python ingest_ng12.py     # One-time PDF ingestion
uvicorn app.main:app --reload

### Frontend
cd frontend
npm install
npm run dev

---

### Documentation 

📄 Documentation

PROMPTS.md – Assessor agent system prompt (Part 1)

CHAT_PROMPTS.md – Conversational agent grounding & guardrails (Part 2)


## 🖥️ User Interface

### NG12 Cancer Risk Assessor
The Assessor UI allows clinicians to input a Patient ID and receive an evidence-based
NG12 referral decision with guideline citations.

![Assessor UI](docs/screenshots/assessor-ui.png)

---

### Conversational NG12 Assistant
The Chat UI enables multi-turn clinical questioning over the NG12 guidelines,
reusing the same RAG pipeline and citation logic.

![Chat UI](docs/screenshots/chat-ui.png)

---

### Evidence & Citations
All clinical statements are grounded in retrieved NG12 passages with page-level citations.

![Citations](docs/screenshots/citations.png)

---

### Summary

This project demonstrates LLM orchestration, grounded RAG design, and clinical-safe reasoning using a single reusable pipeline over structured and unstructured healthcare data.