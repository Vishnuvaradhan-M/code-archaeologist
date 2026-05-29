from rag.vectorstore import query

def limit_text(text: str, max_chars: int = 500) -> str:
    """Trim text to prevent token explosion."""
    if len(text) > max_chars:
        return text[:max_chars] + "..."
    return text

def retrieve(question: str, n: int = 4) -> str:
    """Retrieve relevant code snippets with token-aware limits."""
    results = query(question, n)
    context_parts = []
    for r in results:
        # Trim each chunk to 500 chars max
        trimmed_content = limit_text(r['text'], max_chars=500)
        part = f"[File: {r['metadata'].get('file','?')} | Lines: {r['metadata'].get('lines','?')}]\n{trimmed_content}"
        context_parts.append(part)
    
    context = "\n\n---\n\n".join(context_parts)
    
    # Hard limit total context to 3000 chars
    if len(context) > 3000:
        context = context[:3000] + "\n\n[... additional context truncated ...]"
    
    return context