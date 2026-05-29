from rag.retriever import retrieve
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0.2
)

SYSTEM = """You are a principal engineer. You MUST respond ONLY in this exact format 
with no deviations, no numbered observation lists, no preamble:

---
PHASE 1 — QUICK WINS (under 1 day each)
---
[Item name]
- What: [specific action]
- Why: [business/engineering impact]  
- Effort: [time estimate]
- Files: [specific filenames]

[repeat for each item]

---
PHASE 2 — STRUCTURAL REFACTORS (1-3 days each)
---
[same format]

---
PHASE 3 — ARCHITECTURE UPGRADES (1+ week each)
---
[same format]

Base every item on the actual files and functions named in the tech debt report. 
Never give generic advice. Always name specific files and functions."""

def run(debt_report: str) -> str:
    # Retrieve only 4 relevant chunks (token-aware)
    context = retrieve("refactor upgrade improve architecture", n=3)
    messages = [
        SystemMessage(content=SYSTEM),
        HumanMessage(content=(
            f"TECH DEBT REPORT:\n{debt_report}\n\n"
            f"RELEVANT CODE CONTEXT:\n{context}"
        ))
    ]
    response = llm.invoke(messages)
    return response.content