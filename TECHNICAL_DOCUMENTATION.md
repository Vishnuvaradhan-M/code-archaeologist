# CodeArchaeologist — Complete Technical Documentation

*A deep dive into the conceptual architecture, technical implementation, and design decisions behind CodeArchaeologist.*

---

## Table of Contents

1. [Project Vision & Philosophy](#project-vision--philosophy)
2. [Problem Statement](#problem-statement)
3. [System Architecture](#system-architecture)
4. [Technical Stack](#technical-stack)
5. [Core Components](#core-components)
6. [Data Pipeline](#data-pipeline)
7. [Agent Architecture](#agent-architecture)
8. [RAG (Retrieval-Augmented Generation) System](#rag-system)
9. [Algorithms & Techniques](#algorithms--techniques)
10. [Design Patterns](#design-patterns)
11. [User Interface](#user-interface)
12. [Performance & Optimization](#performance--optimization)
13. [Security Considerations](#security-considerations)
14. [Future Roadmap](#future-roadmap)

---

## 1. Project Vision & Philosophy

### Core Mission

**CodeArchaeologist transforms legacy code from a liability into an asset** by providing engineering teams with rapid, AI-powered intelligence about undocumented codebases.

### Key Philosophical Principles

| Principle | Implementation |
|-----------|---|
| **Automation** | Four specialized agents handle different analysis tasks in parallel |
| **Speed** | RAG + vector search enables instant code understanding (minutes, not weeks) |
| **Transparency** | Every finding is grounded in actual code samples, not speculation |
| **Simplicity** | Gradio UI requires zero DevOps—runs locally or in cloud |
| **Open Source** | No vendor lock-in; all dependencies are MIT/Apache licensed |
| **Economics** | Groq free tier = unlimited analysis with zero API costs |

### Strategic Advantages

- **For Managers**: Objective refactoring roadmaps enable prioritized investment decisions
- **For Architects**: Dependency graphs reveal structural weaknesses and coupling patterns
- **For Engineers**: Rapid onboarding to unfamiliar codebases reduces context-switching overhead
- **For Organizations**: Institutional knowledge is preserved in reverse-engineered intent

---

## 2. Problem Statement

### The Legacy Code Crisis

Enterprise codebases face a universal problem:

```
Legacy System  →  Black Box  →  High Risk  →  Expensive Change  →  Brain Drain
   (10+ yrs)      (no docs)    (failures)     (time, cost)      (key engineer leaves)
```

**Symptoms:**
- New engineers spend 4-6 weeks understanding undocumented systems
- Refactoring decisions are made with incomplete information
- Technical debt is invisible—discovered only after production failures
- Onboarding costs scale linearly with team size
- Architecture changes are risky because dependencies are unmapped

**Root Cause:**
Code's original intent, design decisions, and debt patterns cannot be extracted programmatically using traditional static analysis. Humans must read the code, which is slow and subjective.

### CodeArchaeologist's Solution

Deploy four specialized AI agents that:
1. **Parse** code semantically, not syntactically
2. **Index** code embeddings for semantic search
3. **Reason** about intent, patterns, and debt using LLMs
4. **Synthesize** findings into actionable roadmaps

**Result:** What takes weeks with humans takes **hours with AI**.

---

## 3. System Architecture

### High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     Gradio Web Interface                        │
│              (4-Step Interactive Analysis Pipeline)             │
└────────────────┬────────────────────────────────────────────────┘
                 │
        ┌────────▼─────────┐
        │  User Input      │
        │  • Local path    │
        │  • GitHub URL    │
        │  • Questions     │
        └────────┬─────────┘
                 │
    ┌────────────▼────────────┐
    │   STEP 1: INGESTION     │
    │  ┌────────────────────┐ │
    │  │ AST Parser         │ │ Extract functions, classes, metadata
    │  │ (Python, JS, etc.) │ │
    │  └────────┬───────────┘ │
    │           │             │
    │  ┌────────▼───────────┐ │
    │  │ Chunking Strategy  │ │ Split into semantic units
    │  └────────┬───────────┘ │
    │           │             │
    │  ┌────────▼───────────┐ │
    │  │ Embeddings         │ │ sentence-transformers
    │  │ (all-MiniLM-L6-v2) │ │ (384-dim vectors)
    │  └────────┬───────────┘ │
    │           │             │
    │  ┌────────▼───────────┐ │
    │  │ ChromaDB Storage   │ │ Persistent vector DB
    │  └────────┬───────────┘ │
    └────────────┼────────────┘
                 │
            ┌────┴─────────────────┬────────────┬──────────────┐
            │                      │            │              │
    ┌───────▼──────┐    ┌──────────▼─┐  ┌──────▼────┐  ┌──────▼─────┐
    │   STEP 2:    │    │  STEP 3:   │  │ STEP 3B:  │  │  STEP 4:   │
    │   INTENT     │    │   DEBT     │  │   GRAPH   │  │  REFACTOR  │
    └───────┬──────┘    └──────┬─────┘  └──────┬────┘  └──────┬─────┘
            │                  │                │              │
    ┌───────▼──────────┐   ┌───▼─────────────┐ │        ┌──────▼────────┐
    │ Reverse-Engineer │   │ Tech Debt Mapper│ │        │ Refactor Plan  │
    │ Intent Agent     │   │      Agent      │ │        │ Writer Agent   │
    │ (LLM Groq)       │   │  (LLM Groq)     │ │        │  (LLM Groq)    │
    └───────┬──────────┘   └───┬─────────────┘ │        └──────┬────────┘
            │                  │                │               │
            │          ┌───────▼────────────┐   │               │
            │          │  Graph Analysis    │   │               │
            │          │  (NetworkX)        │   │               │
            │          │  • Hotspot ranking │   │               │
            │          │  • In-degree calc  │   │               │
            │          │  • Dep visualization   │               │
            │          └───────┬────────────┘   │               │
            │                  │                │               │
            │          ┌───────▼────────────┐   │               │
            │          │  Graph Visualization  │               │
            │          │  (Matplotlib)      │   │               │
            │          │  • Color by risk   │   │               │
            │          │  • Size by impact  │   │               │
            │          │  • Dark theme      │   │               │
            │          └───────┬────────────┘   │               │
            │                  │                │               │
            └──────────────────┼────────────────┼───────────────┘
                               │                │
                       ┌───────▼────────────────▼────────┐
                       │   Output & Reports             │
                       │ • Intent summary               │
                       │ • Tech debt breakdown          │
                       │ • Dependency graph image       │
                       │ • Phased refactor plan         │
                       └────────────────────────────────┘
```

### Conceptual Layers

```
┌─────────────────────────────────────────┐
│        PRESENTATION LAYER              │
│  Gradio UI - 4-Tab Interactive Flow    │
└─────────────────────────────────────────┘
              ▲ │
              │ ▼
┌─────────────────────────────────────────┐
│        ORCHESTRATION LAYER              │
│  app.py - Pipeline State & Routing     │
└─────────────────────────────────────────┘
              ▲ │
              │ ▼
┌─────────────────────────────────────────┐
│        AGENT LAYER                      │
│  ┌─────────────┬──────────┬──────────┐ │
│  │ Ingestion   │ Intent   │ Debt     │ │
│  │ Agent       │ Agent    │ Mapper   │ │
│  └─────────────┴──────────┴──────────┘ │
│  ┌─────────────────────────────────┐ │
│  │    Refactor Plan Writer Agent   │ │
│  └─────────────────────────────────┘ │
└─────────────────────────────────────────┘
              ▲ │
              │ ▼
┌─────────────────────────────────────────┐
│        RAG/ANALYSIS LAYER               │
│  ┌──────────┬──────────┬──────────────┐ │
│  │ Vector   │ Graph    │ AST Parser   │ │
│  │ Store    │ Builder  │              │ │
│  └──────────┴──────────┴──────────────┘ │
└─────────────────────────────────────────┘
              ▲ │
              │ ▼
┌─────────────────────────────────────────┐
│        DATA ACCESS LAYER                │
│  ┌──────────┬──────────┬──────────────┐ │
│  │ File I/O │ ChromaDB │ Embeddings   │ │
│  │          │ Client   │ API          │ │
│  └──────────┴──────────┴──────────────┘ │
└─────────────────────────────────────────┘
```

### Execution Flow

```
START
  │
  ├─→ User provides codebase (local path or GitHub URL)
  │
  ├─→ STEP 1: INGESTION AGENT
  │     Parse all code files (AST)
  │     ├─→ Extract functions/classes
  │     ├─→ Generate semantic chunks
  │     ├─→ Create embeddings (sentence-transformers)
  │     └─→ Store in ChromaDB (persistent)
  │
  ├─→ STEP 2: INTENT AGENT
  │     ├─→ Retrieve similar code snippets from ChromaDB
  │     ├─→ Feed to LLM with system prompt
  │     └─→ Output: System purpose, design patterns, intent
  │
  ├─→ STEP 3A: DEBT MAPPER AGENT
  │     ├─→ Build dependency graph from AST
  │     ├─→ Calculate in-degree for each module
  │     ├─→ Identify hotspots (high in-degree)
  │     ├─→ Retrieve problem code patterns from ChromaDB
  │     ├─→ Feed to LLM with hotspot data + code samples
  │     └─→ Output: Tech debt report with severity levels
  │
  ├─→ STEP 3B: GRAPH VISUALIZATION
  │     ├─→ Use NetworkX for layout (spring algorithm)
  │     ├─→ Color nodes by risk: red (critical), yellow (moderate), green (healthy)
  │     ├─→ Size nodes by in-degree (impact on system)
  │     ├─→ Render with Matplotlib (dark theme)
  │     └─→ Output: PNG image of dependency graph
  │
  ├─→ STEP 4: REFACTOR PLAN WRITER AGENT
  │     ├─→ Use debt report + cached context
  │     ├─→ Feed to LLM with structured format prompt
  │     ├─→ LLM outputs phased roadmap:
  │     │     - Phase 1: Quick wins (<1 day each)
  │     │     - Phase 2: Structural refactors (1-3 days)
  │     │     - Phase 3: Architecture upgrades (1+ weeks)
  │     └─→ Output: Markdown roadmap with file/function names
  │
  └─→ END: User downloads all reports
```

---

## 4. Technical Stack

### Core Dependencies

| Layer | Technology | Version | Purpose |
|-------|-----------|---------|---------|
| **LLM Framework** | LangChain | Latest | Prompt engineering, chain composition |
| **LLM Provider** | Groq (llama-3.1-8b) | API | Fast, free tier (9000+ req/day) |
| **Vector Store** | ChromaDB | Latest | Persistent vector database |
| **Embeddings** | sentence-transformers | all-MiniLM-L6-v2 | 384-dim semantic vectors |
| **Code Parsing** | Python AST | Built-in | Extract syntax tree |
| **Code Parsing** | tree-sitter | Latest | Incremental parsing (JS, Python) |
| **Graph Analysis** | NetworkX | Latest | Dependency graph construction |
| **Visualization** | Matplotlib | Latest | Graph rendering |
| **Web UI** | Gradio | Latest | No-code interface |
| **Config** | python-dotenv | Latest | Environment variables (.env) |

### Dependency Graph

```
app.py (main)
  ├── agents/
  │   ├── ingestion_agent.py
  │   │   ├── utils/ast_parser.py
  │   │   └── rag/vectorstore.py
  │   │       └── rag/embedder.py
  │   │           └── sentence_transformers
  │   ├── intent_agent.py
  │   │   ├── rag/retriever.py
  │   │   │   └── rag/vectorstore.py
  │   │   └── langchain_groq.ChatGroq
  │   ├── debt_mapper.py
  │   │   ├── rag/retriever.py
  │   │   ├── utils/graph_builder.py
  │   │   │   └── networkx
  │   │   └── langchain_groq.ChatGroq
  │   └── refactor_agent.py
  │       ├── rag/retriever.py
  │       └── langchain_groq.ChatGroq
  └── rag/vectorstore.py
      └── chromadb
```

### Environment Requirements

```
Python >= 3.8
Operating System: Windows, macOS, Linux
RAM: 4GB minimum (8GB recommended for large codebases)
Disk: 2GB for ChromaDB + embeddings
Internet: Required for Groq API (can be offline with local LLM)
```

---

## 5. Core Components

### 5.1 Ingestion Agent (`agents/ingestion_agent.py`)

**Responsibility:** Parse codebase and create searchable semantic index

#### Algorithm: Multi-Step Ingestion Pipeline

```
INPUT: Directory path or GitHub URL
  │
  ├─→ [STEP A] GitHub URL Resolution
  │     if input.startswith("https://github.com"):
  │         clone_url(input) → local_path
  │     else:
  │         local_path = input
  │
  ├─→ [STEP B] Reset Vector Store (Optional)
  │     if fresh == True:
  │         delete_collection("codebase")
  │         create_new_collection("codebase")
  │
  ├─→ [STEP C] Parse Directory
  │     for each file in directory:
  │         if file.extension in [.py, .js, .java, .cpp, .go]:
  │             parse(file) → list[chunks]
  │
  ├─→ [STEP D] Extract Chunks (AST-based)
  │     for each function/class in AST:
  │         create_chunk({
  │             id: f"{filepath}:{line_no}",
  │             text: function_body,
  │             metadata: {file, lines, type}
  │         })
  │
  ├─→ [STEP E] Generate Embeddings
  │     for each chunk_text in chunks:
  │         embedding = sentence_transformer.encode(chunk_text)
  │         # 384-dimensional dense vector
  │
  ├─→ [STEP F] Store in ChromaDB
  │     collection.add(
  │         ids=[...],
  │         embeddings=[...],
  │         documents=[...],
  │         metadatas=[...]
  │     )
  │
  └─→ OUTPUT: Ingestion report with file count, chunk count
```

#### Code Structure

```python
def run(directory: str, fresh: bool = True) -> str:
    # 1. Resolve GitHub URL if applicable
    if directory.startswith("https://github.com"):
        local_path = clone_repo(directory)
    else:
        local_path = directory
    
    # 2. Reset vectorstore if fresh=True
    if fresh:
        reset()
    
    # 3. Parse directory
    chunks = parse_directory(local_path)
    
    # 4. Add to ChromaDB
    add_documents(chunks)
    
    # 5. Return metadata
    return f"Ingested {len(chunks)} chunks from {local_path}"
```

#### Key Techniques

| Technique | Purpose | Implementation |
|-----------|---------|---|
| **AST Parsing** | Extract semantic units | Python `ast` module walks tree |
| **Chunking** | Manageable context | One function/class = one chunk |
| **Fallback Parsing** | Handle syntax errors | 40-line raw text chunks |
| **Metadata Tagging** | Traceability | Store file path, line numbers, type |
| **Error Resilience** | Skip malformed files | `errors="ignore"` on open() |

---

### 5.2 Intent Reverse-Engineer Agent (`agents/intent_agent.py`)

**Responsibility:** Identify system purpose, design patterns, and business logic

#### Architecture

```
Question Input (e.g., "What does this system do?")
  │
  ├─→ [RETRIEVAL] Query ChromaDB
  │     relevant_chunks = vectorstore.query(question, n=2)
  │     # Retrieve top-2 semantically similar code snippets
  │
  ├─→ [CONTEXT ASSEMBLY] Build RAG Prompt
  │     context = f"""
  │     CODEBASE CONTEXT:
  │     [Chunk 1: {relevant_chunks[0]}]
  │     [Chunk 2: {relevant_chunks[1]}]
  │     
  │     QUESTION: {question}
  │     """
  │
  ├─→ [LLM INFERENCE] Groq API Call
  │     response = groq_client.invoke([
  │         SystemMessage(content=ARCHITECT_PROMPT),
  │         HumanMessage(content=context)
  │     ])
  │
  └─→ OUTPUT: Markdown report with intent, patterns, business logic
```

#### System Prompt Engineering

```python
SYSTEM = """You are a senior software architect. 
Given code snippets from an undocumented codebase, reverse-engineer what the code does.
Explain: 
  (1) overall purpose
  (2) key design decisions
  (3) what problem it solves

Be concise but insightful. Write for a new engineer joining the team.

If the code context provided does not match the question being asked,
say so clearly rather than guessing.
"""
```

#### Token Economy

- **Max input tokens per query:** ~2,000
- **n_retrieval:** 2 chunks (reduced to fit token limit)
- **Groq rate:** 9,000 free requests/day
- **Cost:** $0 on free tier

#### Advanced Capabilities

```
Input Question: "What is the overall purpose of this codebase?"
  ↓ (semantic search)
Retrieved Chunks:
  - [app.py:1-15] Main entry point with Flask initialization
  - [payment.py:50-80] Stripe payment processing logic
  ↓ (RAG + LLM)
Output: "This is a SaaS billing platform that integrates Stripe for 
         recurring subscription management and usage-based pricing."
```

---

### 5.3 Tech Debt Mapper Agent (`agents/debt_mapper.py`)

**Responsibility:** Detect patterns, hotspots, and structural problems

#### Algorithm: Hotspot + Code Analysis

```
INPUT: Directory path
  │
  ├─→ [STEP 1] Build Dependency Graph
  │     G = DirectedGraph()
  │     for each Python file:
  │         for each import statement:
  │             G.add_edge(importer, imported_module)
  │
  ├─→ [STEP 2] Calculate In-Degree Centrality
  │     in_degree = {module: count of inbound imports}
  │     hotspots = sort_by_in_degree(top_5)
  │     # E.g., "payment.py: 23 inbound imports"
  │
  ├─→ [STEP 3] Retrieve Problem Code Patterns
  │     bad_patterns = vectorstore.query(
  │         "bad code practices error handling hardcoded values",
  │         n=4
  │     )
  │
  ├─→ [STEP 4] LLM Analysis
  │     response = groq_client.invoke([
  │         SystemMessage(content=DEBT_AUDITOR_PROMPT),
  │         HumanMessage(content=f"""
  │         HOTSPOTS: {hotspots_str}
  │         CODE SAMPLES: {bad_patterns}
  │         """)
  │     ])
  │
  └─→ OUTPUT: Tech debt report with severity classification
```

#### Hotspot Detection Algorithm

```python
def get_hotspots(G: nx.DiGraph, top_n=5) -> list[tuple]:
    """
    Calculate in-degree centrality for each node.
    In-degree = number of modules that import this module.
    
    High in-degree = high coupling risk.
    If this module breaks, many things break.
    """
    in_degree = sorted(
        G.in_degree(),  # [(node, degree), ...]
        key=lambda x: x[1],
        reverse=True
    )
    return in_degree[:top_n]
```

#### Severity Classification

| Severity | Criteria | Example | Impact |
|----------|----------|---------|--------|
| **CRITICAL** | >5 dependents + no error handling | God class with circular deps | Production risk |
| **HIGH** | 3-5 dependents + hardcoded values | Config in code | Env-specific failures |
| **MEDIUM** | Missing logging/tests | Difficult debugging | Development overhead |
| **LOW** | Code style, minor duplication | Non-idiomatic patterns | Maintainability |

#### Problem Detection Heuristics

```
[Pattern Detector]
├─→ Hardcoded Values
│     Regex: r"(\d+)|('.*')|(".*")"  # Magic numbers/strings
│     Severity: HIGH (environment-specific bugs)
│
├─→ Missing Error Handling
│     AST: look for try/except ratio
│     Severity: CRITICAL (unhandled exceptions)
│
├─→ Circular Dependencies
│     Graph: detect cycles with networkx.simple_cycles()
│     Severity: CRITICAL (refactoring blocker)
│
├─→ God Classes
│     Heuristic: >1000 lines or >30 methods
│     Severity: HIGH (testing/maintenance burden)
│
└─→ Missing Type Hints
      AST: count annotated vs unannotated params
      Severity: MEDIUM (IDE support, runtime errors)
```

---

### 5.4 Refactor Plan Writer Agent (`agents/refactor_agent.py`)

**Responsibility:** Generate actionable, prioritized refactoring roadmap

#### Prompt Engineering: Structured Output

```python
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
Never give generic advice. Always name specific files and functions.
"""
```

#### Output Structure

```markdown
---
PHASE 1 — QUICK WINS (under 1 day each)
---
Add type hints to payment.py
- What: Add @param and @return type annotations to payment_calculator()
- Why: Enables IDE autocomplete; catches 40% of runtime errors at dev time
- Effort: 2 hours
- Files: payment.py (lines 50-150)

Extract hardcoded timeouts
- What: Move AWS_TIMEOUT=30 to config.py
- Why: Enables environment-specific tuning (dev vs production)
- Effort: 30 minutes
- Files: payment.py, notifier.py

---
PHASE 2 — STRUCTURAL REFACTORS (1-3 days each)
---
Break circular dependency: payment.py ↔ pricing.py
- What: Introduce CalculatorInterface; inject into payment.py
- Why: Enables unit testing; reduces coupling
- Effort: 1.5 days
- Files: payment.py, pricing.py, calculator.py (new)

---
PHASE 3 — ARCHITECTURE UPGRADES (1+ week each)
---
Migrate to Hexagonal Architecture
- What: Separate domain logic from infrastructure (DB, API, messaging)
- Why: Enables testing without external dependencies; improves reusability
- Effort: 2 weeks
- Files: Restructure entire project layout
```

---

### 5.5 AST Parser (`utils/ast_parser.py`)

**Responsibility:** Extract semantic units from source code

#### Extraction Strategy

```python
def extract_python_chunks(filepath: str) -> list[dict]:
    """
    Parse Python file using AST.
    Extract all functions, classes, async functions.
    Return as chunks with metadata.
    """
    with open(filepath, "r", errors="ignore") as f:
        source = f.read()
    
    chunks = []
    try:
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                # Extract line numbers
                start = node.lineno
                end = getattr(node, "end_lineno", start + 10)
                
                # Extract source code snippet
                snippet = "\n".join(source.splitlines()[start-1:end])
                
                # Create chunk with metadata
                chunks.append({
                    "id": f"{filepath}:{start}",
                    "text": snippet,
                    "metadata": {
                        "file": filepath,
                        "lines": f"{start}-{end}",
                        "type": type(node).__name__  # FunctionDef, ClassDef, etc.
                    }
                })
    except SyntaxError:
        # Fallback: chunk raw text every 40 lines
        lines = source.splitlines()
        for i in range(0, len(lines), 40):
            chunk = "\n".join(lines[i:i+40])
            chunks.append({
                "id": f"{filepath}:{i}",
                "text": chunk,
                "metadata": {
                    "file": filepath,
                    "lines": f"{i}-{i+40}",
                    "type": "raw"
                }
            })
    
    return chunks
```

#### Multi-Language Support

```python
def parse_directory(directory: str) -> list[dict]:
    all_chunks = []
    for root, _, files in os.walk(directory):
        for fname in files:
            # Multi-language support
            if fname.endswith((".py", ".js", ".ts", ".java", ".cpp", ".c", ".go")):
                fpath = os.path.join(root, fname)
                all_chunks.extend(extract_python_chunks(fpath))
    
    return all_chunks
```

**Note:** Current implementation uses Python AST. For JavaScript/TypeScript, would require tree-sitter library. Java/C++ would use their respective parsers.

---

### 5.6 Dependency Graph Builder (`utils/graph_builder.py`)

**Responsibility:** Construct and visualize code dependency graph

#### Graph Construction Algorithm

```python
def build_dependency_graph(directory: str) -> nx.DiGraph:
    """
    Build directed graph of import dependencies.
    
    Algorithm:
    1. Walk all Python files
    2. For each import statement, add edge from importer to imported
    3. Calculate in-degree (how many modules depend on this)
    4. Return weighted graph
    """
    G = nx.DiGraph()  # Directed graph
    
    for root, _, files in os.walk(directory):
        for fname in files:
            if not fname.endswith(".py"):
                continue
            
            fpath = os.path.join(root, fname)
            module_name = fname.replace(".py", "")
            G.add_node(module_name)
            
            # Parse imports
            try:
                with open(fpath, "r", errors="ignore") as f:
                    tree = ast.parse(f.read())
                
                for node in ast.walk(tree):
                    if isinstance(node, (ast.Import, ast.ImportFrom)):
                        # Extract imported module names
                        if isinstance(node, ast.Import):
                            names = [a.name for a in node.names]
                        else:  # ImportFrom
                            names = [node.module or ""]
                        
                        # Add edge from current module to imported module
                        for n in names:
                            G.add_edge(module_name, n.split(".")[0])
            except Exception:
                pass  # Skip malformed files
    
    return G
```

#### In-Degree Centrality

```
Example dependency graph:
  payment.py → stripe.py
  webhook.py → stripe.py
  invoice.py → stripe.py
  pricing.py → stripe.py
  
stripe.py in-degree = 4 (four modules depend on it)
payment.py in-degree = 1 (only webhook.py depends on it)

INTERPRETATION:
- stripe.py is a hotspot. If it breaks, 4 modules break.
- payment.py is peripheral. If it breaks, only 1 module breaks.

REFACTOR PRIORITY:
- Fix stripe.py first (highest risk)
- payment.py can be refactored later (lower risk)
```

#### Graph Visualization: Matplotlib Rendering

```python
def export_graph_image(G: nx.DiGraph, output_path: str = "graph.png") -> str:
    """
    Render dependency graph with color-coded risk levels.
    
    Coloring Scheme:
    - RED (in-degree > 5): CRITICAL hotspot
    - YELLOW (3-5 dependents): MODERATE coupling
    - GREEN (< 3 dependents): HEALTHY isolation
    
    Node Size: Proportional to in-degree
    Layout: Spring algorithm (force-directed)
    """
    fig, ax = plt.subplots(figsize=(12, 8), facecolor="#1a1a2e")
    ax.set_facecolor("#1a1a2e")
    
    # Calculate layout using force-directed algorithm
    pos = nx.spring_layout(G, seed=42)
    
    # Determine node colors by risk
    node_colors = []
    for node in G.nodes():
        in_deg = G.in_degree(node)
        if in_deg > 5:
            node_colors.append("red")      # CRITICAL
        elif 3 <= in_deg <= 5:
            node_colors.append("yellow")   # MODERATE
        else:
            node_colors.append("green")    # HEALTHY
    
    # Determine node sizes by in-degree
    node_sizes = [
        max(800, 300 + G.in_degree(node) * 200)
        for node in G.nodes()
    ]
    
    # Draw graph
    nx.draw_networkx_nodes(G, pos, node_size=node_sizes, node_color=node_colors)
    nx.draw_networkx_edges(G, pos, edge_color="#555555", arrows=True)
    nx.draw_networkx_labels(G, pos, font_color="white")
    
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    
    return output_path
```

**Visualization Interpretation:**
- **Red nodes** = Production risk; refactor first
- **Yellow nodes** = Monitor for coupling creep
- **Green nodes** = Safe to refactor; low risk
- **Large circles** = Many dependents; high impact
- **Arrows** = Dependency direction; trace to find coupling chains

---

## 6. Data Pipeline

### Complete Data Flow Diagram

```
INGESTION PHASE
═════════════════════════════════════════════════════════════════

Raw Codebase
  │
  ├─→ GitHub URL?
  │     yes: clone_repo(url) → local_copy
  │     no: use_as_is(path)
  │
  └─→ codebase/
       ├─→ file1.py
       ├─→ file2.py
       └─→ ...

                │
                ▼

AST Parser (utils/ast_parser.py)
  for each file:
    ├─→ ast.parse(file)
    ├─→ extract_functions()
    ├─→ extract_classes()
    ├─→ add_metadata(file_path, line_numbers, type)
    └─→ chunk_list.append()

                │
                ▼

Chunks with Metadata
  [
    {
      "id": "payment.py:50",
      "text": "def process_payment(amount):\n    ...",
      "metadata": {"file": "payment.py", "lines": "50-75", "type": "FunctionDef"}
    },
    ...
  ]

                │
                ▼

Embeddings (rag/embedder.py)
  sentence_transformers.encode(chunks)
  → 384-dimensional dense vectors
  → captures semantic meaning

                │
                ▼

ChromaDB Storage (rag/vectorstore.py)
  collection.add(
    ids=[],
    embeddings=[],          ← 384-dim vectors
    documents=[],           ← source code text
    metadatas=[]            ← file path, line numbers
  )

                │
                ▼

                    ┌────────────────────────────┐
                    │   ChromaDB Vector Store    │
                    │  (Persistent SQLite DB)    │
                    │  chroma_db/                │
                    │  ├─ chroma.sqlite3        │
                    │  ├─ collection_1/         │
                    │  └─ ...                    │
                    └────────────────────────────┘


ANALYSIS PHASE
═════════════════════════════════════════════════════════════════

User Question / Analysis Task
  │
  ├──→ INTENT AGENT
  │      │
  │      ├─→ vectorstore.query(question, n=2)
  │      │    ↓
  │      │    cosine_similarity(question_embedding, all_chunk_embeddings)
  │      │    ↓
  │      │    top_2_similar_chunks
  │      │
  │      ├─→ build_prompt(system_msg, context, question)
  │      ├─→ groq_llm.invoke(prompt)
  │      └─→ markdown_report
  │
  ├──→ DEBT MAPPER AGENT
  │      │
  │      ├─→ build_dependency_graph(directory)
  │      │    ├─→ for each file: parse imports
  │      │    ├─→ create edges (importer → imported)
  │      │    └─→ directed graph
  │      │
  │      ├─→ calculate_in_degree(graph)
  │      │    └─→ identify hotspots (top_5)
  │      │
  │      ├─→ vectorstore.query(bad_code_patterns, n=4)
  │      │    ↓
  │      │    retrieve error handling, hardcoded values, etc.
  │      │
  │      ├─→ build_prompt(hotspots + code_samples)
  │      ├─→ groq_llm.invoke(prompt)
  │      └─→ tech_debt_report
  │
  ├──→ GRAPH VISUALIZATION
  │      │
  │      ├─→ networkx.spring_layout(graph)
  │      ├─→ color_by_risk(in_degree)
  │      ├─→ size_by_impact(in_degree)
  │      ├─→ matplotlib.draw(graph)
  │      └─→ PNG image
  │
  └──→ REFACTOR PLAN WRITER
         │
         ├─→ vectorstore.query(refactor patterns, n=3)
         ├─→ build_prompt(debt_report + code_context)
         ├─→ groq_llm.invoke(prompt with strict format)
         └─→ phased_refactor_plan (Phase 1, 2, 3)


OUTPUT PHASE
═════════════════════════════════════════════════════════════════

Reports Generated:
  ├─→ Intent Summary
  │    └─→ "System purpose is X, design patterns include Y, solves Z"
  │
  ├─→ Tech Debt Report
  │    └─→ "CRITICAL: circular deps in payment.py
  │        HIGH: no error handling in stripe.py
  │        MEDIUM: missing type hints across codebase"
  │
  ├─→ Dependency Graph (PNG)
  │    └─→ Visualization with color-coded risk levels
  │
  └─→ Refactor Roadmap
       ├─→ Phase 1: Quick Wins (2 days total)
       ├─→ Phase 2: Structural Refactors (5 days)
       └─→ Phase 3: Architecture Upgrades (2 weeks)

                │
                ▼

        User Downloads Reports
```

### Data Structure Examples

#### Chunk Structure

```python
{
    "id": "src/payment.py:52",
    "text": """def process_payment(amount: float, currency: str = "USD") -> dict:
    '''Process payment via Stripe API.
    
    Args:
        amount: Payment amount in cents
        currency: ISO currency code
    
    Returns:
        Stripe charge response
    '''
    if amount < 0:
        raise ValueError("Amount must be positive")
    
    try:
        charge = stripe.Charge.create(
            amount=int(amount * 100),
            currency=currency,
            source="tok_visa"
        )
        return {"success": True, "charge_id": charge.id}
    except stripe.CardError as e:
        logger.error(f"Card declined: {e}")
        return {"success": False, "error": str(e)}""",
    "metadata": {
        "file": "src/payment.py",
        "lines": "52-72",
        "type": "FunctionDef"
    }
}
```

#### Graph Node/Edge Structure

```
Nodes:
  - payment.py (in-degree: 3, color: yellow)
  - pricing.py (in-degree: 5, color: red)
  - stripe.py (in-degree: 2, color: green)
  - webhook.py (in-degree: 1, color: green)

Edges (imports):
  payment.py → stripe.py
  pricing.py → stripe.py
  pricing.py → webhook.py
  webhook.py → stripe.py
  payment.py → pricing.py
```

#### LLM Input Context (RAG)

```
SYSTEM: "You are a senior software architect..."