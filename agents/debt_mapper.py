from rag.retriever import retrieve
from utils.graph_builder import build_dependency_graph, get_hotspots
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
import os

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0.2
)

SYSTEM = """You are a tech debt auditor. 
Given code snippets, identify:
1. Tech debt hotspots (God classes, long functions, no error handling, hardcoded values)
2. Dependency smell (circular imports, tight coupling)  
3. Missing patterns (no logging, no tests detected, no type hints)
Return a structured report with severity: CRITICAL / HIGH / MEDIUM / LOW.
IMPORTANT: Only report issues found in the CODE SAMPLES provided below. 
Do not invent or assume file names. If you reference a file, it must appear 
in the CODE SAMPLES section. If a pattern is missing (no tests, no logging), 
confirm this by noting the absence in the provided samples, not by assumption."""

def run(directory: str) -> str:
    G = build_dependency_graph(directory)
    hotspots = get_hotspots(G, top_n=5)
    hotspot_str = "\n".join(f"  - {mod}: {deg} dependents" for mod, deg in hotspots)

    # Retrieve only 4 relevant chunks (token-aware)
    context = retrieve("bad code practices error handling hardcoded values", n=4)
    messages = [
        SystemMessage(content=SYSTEM),
        HumanMessage(content=(
            f"DEPENDENCY HOTSPOTS (most imported modules):\n{hotspot_str}\n\n"
            f"CODE SAMPLES:\n{context}"
        ))
    ]
    response = llm.invoke(messages)
    return f"DEPENDENCY HOTSPOTS:\n{hotspot_str}\n\n---\n\nTECH DEBT REPORT:\n{response.content}"