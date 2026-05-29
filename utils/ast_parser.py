import ast, os

def extract_python_chunks(filepath: str) -> list[dict]:
    with open(filepath, "r", errors="ignore") as f:
        source = f.read()
    chunks = []
    try:
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                start = node.lineno
                end = getattr(node, "end_lineno", start + 10)
                snippet = "\n".join(source.splitlines()[start-1:end])
                chunks.append({
                    "id": f"{filepath}:{start}",
                    "text": snippet,
                    "metadata": {"file": filepath, "lines": f"{start}-{end}", "type": type(node).__name__}
                })
    except SyntaxError:
        # fallback: chunk raw text every 40 lines
        lines = source.splitlines()
        for i in range(0, len(lines), 40):
            chunk = "\n".join(lines[i:i+40])
            chunks.append({
                "id": f"{filepath}:{i}",
                "text": chunk,
                "metadata": {"file": filepath, "lines": f"{i}-{i+40}", "type": "raw"}
            })
    return chunks

def parse_directory(directory: str) -> list[dict]:
    all_chunks = []
    for root, _, files in os.walk(directory):
        for fname in files:
            if fname.endswith((".py", ".js", ".ts", ".java", ".cpp", ".c", ".go")):
                fpath = os.path.join(root, fname)
                all_chunks.extend(extract_python_chunks(fpath))
    return all_chunks