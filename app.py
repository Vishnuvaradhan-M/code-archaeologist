import gradio as gr
import os
import chromadb
import subprocess
import shutil
from dotenv import load_dotenv
load_dotenv()

from agents.ingestion_agent import run as ingest
from agents.intent_agent import run as reverse_engineer
from agents.debt_mapper import run as map_debt
from agents.refactor_agent import run as write_refactor
from rag.vectorstore import reset

# --- pipeline state ---
debt_report_cache = {"value": ""}
active_dir_cache = {"path": ""}

def clone_if_github(source: str) -> str:
    """Clone GitHub repository if source is a GitHub URL, otherwise return source unchanged."""
    if source.startswith("https://github.com"):
        # Extract repo name from URL
        repo_name = source.rstrip("/").split("/")[-1]
        if repo_name.endswith(".git"):
            repo_name = repo_name[:-4]
        
        # Create local directory path
        local_path = os.path.join("cloned_repos", repo_name)
        
        # Delete existing directory if it exists
        if os.path.exists(local_path):
            shutil.rmtree(local_path)
        
        # Clone the repository
        try:
            subprocess.run(["git", "clone", source, local_path], check=True, capture_output=True)
        except subprocess.CalledProcessError:
            return "Git clone failed. Make sure git is installed and the repository URL is public."
        except FileNotFoundError:
            return "Git is not installed or not in PATH. Install git from https://git-scm.com"
        
        return local_path
    
    return source

def step1_ingest(directory):
    # Reset vectorstore first to ensure clean state when switching repos
    reset()
    
    if not os.path.isdir(directory) and not directory.startswith("https://github.com"):
        return "Directory not found. Please enter a valid path or GitHub URL.", gr.update(interactive=False)
    result = ingest(directory)
    # Store resolved path — if github url, ingestion_agent clones to cloned_repos/reponame
    if directory.startswith("https://github.com"):
        repo_name = directory.rstrip("/").split("/")[-1].replace(".git", "")
        active_dir_cache["path"] = os.path.join("cloned_repos", repo_name)
    else:
        active_dir_cache["path"] = directory
    return result, gr.update(interactive=True)

def step2_intent(question):
    return reverse_engineer(question)

def step3_debt(directory):
    resolved = directory.strip() if directory.strip() else active_dir_cache["path"]
    if not resolved:
        return "Please run Step 1 first.", gr.update(interactive=False), gr.update(visible=False)
    from utils.graph_builder import build_dependency_graph, export_graph_image
    report = map_debt(resolved)
    debt_report_cache["value"] = report
    G = build_dependency_graph(resolved)
    img_path = export_graph_image(G, "graph.png")
    return report, gr.update(interactive=True), gr.update(visible=True, value=img_path)

def step4_refactor():
    return write_refactor(debt_report_cache["value"])

def reset_vectorstore():
    try:
        client = chromadb.Client()
        client.delete_collection("codebase")
        return "✓ Vectorstore reset successfully. Old collection deleted."
    except Exception as e:
        return f"✓ Reset complete (collection may not have existed). Ready for new codebase.\nDetails: {str(e)}"

def handle_proceed():
    return gr.update(selected=1)

with gr.Blocks(title="CodeArchaeologist", theme=gr.themes.Soft()) as demo:
    gr.Markdown("""
# CodeArchaeologist
### Multi-Agent Legacy Codebase Intelligence System
Upload or point to any codebase. Four AI agents will read it, understand it, find its debt, and write your upgrade plan.
---
""")

    with gr.Tabs() as tabs:
        with gr.Tab("Step 1 — Ingest Codebase", id=0):
            gr.Markdown("Paste a **local folder path** or a **public GitHub URL** — the system will auto-clone and analyze any public repository.")
            reset_btn = gr.Button("🔄 Reset Vectorstore", variant="stop")
            reset_out = gr.Textbox(label="Reset status", interactive=False)
            reset_btn.click(reset_vectorstore, outputs=reset_out)
            gr.Markdown("---")
            dir_input = gr.Textbox(label="Local path or GitHub URL", placeholder="e.g. test_repo   OR   https://github.com/username/repo", value="test_repo")
            gr.Markdown("Paste a GitHub URL to auto-clone and analyze any public repository.")
            ingest_btn = gr.Button("Run Ingestion Agent", variant="primary")
            ingest_out = gr.Textbox(label="Agent 1 output", lines=6)
            proceed_btn = gr.Button("Proceed to analysis", interactive=False)
            ingest_btn.click(step1_ingest, inputs=dir_input, outputs=[ingest_out, proceed_btn])
            proceed_btn.click(fn=handle_proceed, inputs=None, outputs=tabs)

        with gr.Tab("Step 2 — Reverse-Engineer Intent", id=1):
            gr.Markdown("Ask the Intent Agent anything about what this codebase does.")
            q_input = gr.Textbox(
                label="Your question",
                value="What is the overall purpose of this codebase and its main design patterns?",
                lines=2
            )
            intent_btn = gr.Button("Run Intent Agent", variant="primary")
            intent_out = gr.Markdown(label="Agent 2 output — codebase intent")
            intent_btn.click(step2_intent, inputs=q_input, outputs=intent_out)

        with gr.Tab("Step 3 — Map Tech Debt", id=2):
            gr.Markdown("The Debt Mapper Agent scans for hotspots, anti-patterns, and structural smells.")
            dir_input2 = gr.Textbox(label="Same directory path as Step 1", placeholder="Local path e.g. test_repo  OR  https://github.com/username/repo", value="test_repo")
            gr.Markdown("Paste a GitHub URL to auto-clone and analyze any public repository.")
            debt_btn = gr.Button("Run Debt Mapper Agent", variant="primary")
            debt_out = gr.Markdown(label="Agent 3 output — tech debt report")
            graph_img = gr.Image(label="Dependency Graph — Module Hotspots", visible=False)
            gr.Markdown("""
### How to read this graph
- 🔴 **Red node** = Critical hotspot (5+ modules depend on it) — highest refactor risk  
- 🟡 **Yellow node** = Moderate coupling (3-5 dependents) — monitor closely  
- 🟢 **Green node** = Healthy (under 3 dependents) — low risk  
- **Bigger circle** = more modules import it — if it breaks, more things break  
- **Arrows** show import direction — follow arrows to trace dependency chains
""")
            refactor_btn = gr.Button("Generate refactor plan", interactive=False, variant="secondary")
            debt_btn.click(step3_debt, inputs=dir_input2, outputs=[debt_out, refactor_btn, graph_img])
            # Auto-populate dir_input2 when Step 1 ingestion completes
            ingest_btn.click(lambda d: d, inputs=dir_input, outputs=dir_input2)

        with gr.Tab("Step 4 — Refactor Plan", id=3):
            gr.Markdown("The Refactor Writer Agent produces a phased engineering upgrade spec.")
            refactor_btn2 = gr.Button("Run Refactor Writer Agent", variant="primary")
            refactor_out = gr.Markdown(label="Agent 4 output — phased upgrade roadmap")
            refactor_btn2.click(step4_refactor, outputs=refactor_out)
            gr.Markdown("---\n*Export this as your README-REFACTOR.md or paste directly into Notion/Confluence.*")

    gr.Markdown("""
---
**Stack:** LangChain · Groq (llama3-8b-8192) · ChromaDB · sentence-transformers · NetworkX · Gradio  
**Open source · Zero API cost on Groq free tier**
""")

demo.launch(share=True)