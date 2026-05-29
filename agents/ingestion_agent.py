import subprocess
import os
from utils.ast_parser import parse_directory
from rag.vectorstore import add_documents, reset

def run(directory: str, fresh: bool = True) -> str:
    # Detect if input is a GitHub URL
    is_github_url = directory.startswith("https://github.com")
    resolved_path = directory
    
    if is_github_url:
        # Extract repo name from URL
        repo_name = directory.rstrip("/").split("/")[-1]
        if repo_name.endswith(".git"):
            repo_name = repo_name[:-4]
        
        # Create temp_repos folder if it doesn't exist
        temp_repos_dir = "temp_repos"
        os.makedirs(temp_repos_dir, exist_ok=True)
        
        # Set local path
        local_path = os.path.join(temp_repos_dir, repo_name)
        
        # Clone if not already present
        if not os.path.exists(local_path):
            subprocess.run(["git", "clone", directory, local_path], check=True)
        
        resolved_path = local_path
        source_type = f"GitHub URL (cloned to {local_path})"
    else:
        source_type = "Local directory"
    
    # Clear old data if fresh=True
    if fresh:
        reset()
    
    # Parse directory and add documents
    chunks = parse_directory(resolved_path)
    if not chunks:
        return "No supported source files found."
    
    add_documents(chunks)
    
    return (
        f"Ingestion complete.\n"
        f"- Source: {source_type}\n"
        f"- Resolved path: {resolved_path}\n"
        f"- Files parsed and chunked: {len(chunks)} segments\n"
        f"- Stored in ChromaDB vector store\n"
        f"- Ready for RAG queries"
    )