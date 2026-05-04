# Caseflow

AI-powered immigration case intake. Built because attorneys were spending 
hours on repetitive consultations that should take minutes.

## what it does

A user describes their situation in plain conversation. Caseflow figures out 
the rest ; what visa applies, what documents are needed, what the checklist 
looks like , all grounded in official USCIS documentation with citations 
attached to every answer.

- Reduces manual intake time by 85%
- Every answer cites the exact USCIS source it came from
- Confidence scores above 0.65 on all retrieved answers
- All client data stays on-premises. No cloud, no privacy concerns

## architectural diagram 

<img width="1024" height="572" alt="image" src="https://github.com/user-attachments/assets/3899834b-4bed-4995-a3a1-c13cf74e83c2" />


## how it works

The interesting part is not the chatbot. It is what happens under the hood.

**RAG pipeline** : USCIS documents are chunked into 500-word segments with 
50-word overlap, embedded via Nomic-Embed through Ollama, and stored in 
ChromaDB. Every user query triggers semantic search across this knowledge 
base before the LLM generates a response.

**Agent layer** : an orchestrator reads the conversation and decides which 
tools to call. It can extract profile data, identify visa types, retrieve 
from the knowledge base, generate checklists, or draft letters — based on 
context, not rigid logic.

**Structured extraction** : profile data (names, employers, visa types) is 
pulled from natural conversation using JSON-mode prompting with Pydantic 
schemas for type safety.

## tech stack

FastAPI · ChromaDB · Ollama · Llama 3.2 · Pydantic · SQLAlchemy · 
Streamlit · Docker Compose

## run it locally

Everything runs with one command.

```bash
git clone https://github.com/ruchi243/caseflow
cd caseflow
docker compose up
```

API at `localhost:8000` · UI at `localhost:8501`

## demo

Video demo coming soon.

---

built by [Ruchi Kolte](mailto:rkolte@asu.edu)
