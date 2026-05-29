from rag.retriever import retrieve
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0.2
)

SYSTEM = """You are a senior software architect. 
Given code snippets from an undocumented codebase, reverse-engineer what the code does.
Explain: (1) overall purpose, (2) key design decisions, (3) what problem it solves.
Be concise but insightful. Write for a new engineer joining the team.
If the code context provided does not match the question being asked about 
a specific codebase, say so clearly rather than guessing."""

def run(question: str = "What is the overall purpose of this codebase?") -> str:
    # Retrieve only 2 relevant chunks (token-aware)
    context = retrieve(question, n=2)
    if not context.strip():
        return "No codebase has been ingested yet. Please run Step 1 first."
    messages = [
        SystemMessage(content=SYSTEM),
        HumanMessage(content=f"CODEBASE CONTEXT:\n{context}\n\nQUESTION: {question}")
    ]
    response = llm.invoke(messages)
    return response.content