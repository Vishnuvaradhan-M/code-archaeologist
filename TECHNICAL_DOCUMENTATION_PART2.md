# CodeArchaeologist — Extended Technical Documentation (Part 2)

*Continuation of comprehensive technical details*

---

## 7. Agent Architecture (Detailed)

### Agent Design Pattern

All four agents follow the same orchestration pattern:

```python
# Universal Agent Pattern
def run(input_data: str) -> str:
    # 1. Prepare context (retrieve + assemble)
    context = prepare_context(input_data)
    
    # 2. Build prompt
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=context)
    ]
    
    # 3. Invoke LLM
    response = llm.invoke(messages)
    
    # 4. Return markdown
    return response.content
```

### Agent Specialization Matrix

| Agent | System Prompt | Input | Output | Token Budget |
|-------|---------------|-------|--------|--------------|
| **Ingestion** | None (no LLM) | Codebase dir | Chunk count | N/A |
| **Intent** | Architect lens | Question + code | System purpose | 2,000 |
| **Debt** | Auditor lens | Hotspots + code | Severity report | 2,500 |
| **Refactor** | Principal engineer lens | Debt report + code | Phased roadmap | 2,000 |

### Multi-Agent Orchestration (app.py)

```python
# State Machine: Sequential Execution with Caching

debt_report_cache = {"value": ""}    # Debt output → Refactor input
active_dir_cache = {"path": ""}      # Ingestion output → other agents

with gr.Blocks() as demo:
    with gr.Tabs() as tabs:
        # Tab 0: INGESTION (state: initialized)
        ingest_btn.click(
            fn=step1_ingest,
            inputs=dir_input,
            outputs=[ingest_out, proceed_btn]
        )
        # Side effects:
        #   - populate active_dir_cache["path"]
        #   - reset ChromaDB
        #   - build embeddings
        #   - enable "Proceed" button
        
        # Tab 1: INTENT (state: analyzed_intent)
        intent_btn.click(
            fn=step2_intent,
            inputs=q_input,
            outputs=intent_out
        )
        # Input: question from user
        # Side effects: none (read-only query)
        
        # Tab 2: DEBT (state: debt_analyzed)
        debt_btn.click(
            fn=step3_debt,
            inputs=dir_input2,
            outputs=[debt_out, refactor_btn, graph_img]
        )
        # Side effects:
        #   - populate debt_report_cache["value"]
        #   - build_dependency_graph()
        #   - render graph visualization
        #   - enable "Generate refactor plan" button
        
        # Tab 3: REFACTOR (state: roadmap_generated)
        refactor_btn2.click(
            fn=step4_refactor,
            inputs=debt_report_cache["value"],
            outputs=refactor_out
        )
        # Input: cached debt report
        # Side effects: none (read-only query)
```

---

## 8. RAG (Retrieval-Augmented Generation) System

### RAG Architecture

```
RAG = Retrieval + Augmented + Generation

                    ┌─────────────────────────────┐
                    │  Vector Store (ChromaDB)    │
                    │  ┌───────────────────────┐  │
                    │  │ Embeddings Index      │  │
                    │  │ (384-dim vectors)     │  │
                    │  ├───────────────────────┤  │
                    │  │ Chunk 1: 384 floats   │  │
                    │  │ Chunk 2: 384 floats   │  │
                    │  │ Chunk N: 384 floats   │  │
                    │  └───────────────────────┘  │
                    └──────────────┬───────────────┘
                                   │
                    ┌──────────────▼────────────────┐
                    │ Semantic Search Layer        │
                    │ (Cosine Similarity)          │
                    └──────────────┬────────────────┘
                                   │
    User Query ──────────────────▶ │
                                   │
    Query Embedding:               │
    "error handling"               │
    ↓                              │
    Encode with                    │
    all-MiniLM-L6-v2               │
    ↓                              │
    384-dim vector                 │
    ↓                              │
    Compare with ─────────────────▶ Cosine Similarity
    all chunks                      ↓
                           ┌────────┴─────────┐
                           │ Ranked Results   │
                           │ (top_k chunks)   │
                           └────────┬─────────┘
                                    │
                    ┌───────────────▼────────────────┐
                    │ Prompt Assembly (RAG Context)  │
                    │                                │
                    │ SYSTEM: "You are an X..."     │
                    │ HUMAN: "Query + [Chunks]"     │
                    └────────────────┬───────────────┘
                                     │
                                     ▼
                        ┌────────────────────────┐
                        │  LLM (Groq llama-3.1)  │
                        │                        │
                        │  Input: 2K tokens      │
                        │  Output: ~500 tokens   │
                        └────────────┬───────────┘
                                     │
                                     ▼
                          Final Response (Markdown)
```

### RAG Advantages Over Pure LLM

| Aspect | Pure LLM | RAG | Benefit |
|--------|----------|-----|---------|
| **Hallucination** | High (invents code) | Low (grounded) | Factual accuracy |
| **Context Window** | 8K tokens | Filtered 2K | Token efficiency |
| **Latency** | 2-3 seconds | 1-2 seconds | Faster responses |
| **Relevance** | General | Specific (code) | Precise analysis |
| **Cost** | High | Low | Reduced API calls |

### Embedding Model: all-MiniLM-L6-v2

```
Model Name: all-MiniLM-L6-v2
Hugging Face: https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2

Architecture:
  - Based on MiniLM (Microsoft lightweight distilled BERT)
  - 6 layers, 384 hidden dimensions
  - Trained on 215M sentence pairs
  
Performance:
  - Encoding speed: ~1000 sentences/sec (GPU)
  - Model size: 22 MB
  - Memory: ~35 MB loaded
  
Strengths:
  - Fast inference (suitable for real-time search)
  - Small model size (no large GPU needed)
  - Strong semantic understanding of code + natural language
  - Well-tested on similarity/retrieval tasks

Code Example:
  from sentence_transformers import SentenceTransformer
  model = SentenceTransformer("all-MiniLM-L6-v2")
  
  embedding1 = model.encode("def calculate_payment(amount):")
  embedding2 = model.encode("payment calculation")
  
  # Cosine similarity: 0.85 (semantically similar)
  similarity = embedding1 @ embedding2 / (norm(embedding1) * norm(embedding2))
```

### ChromaDB: Persistent Vector Store

```
ChromaDB Architecture:

┌──────────────────────────────────────────────┐
│  ChromaDB Client (Python API)               │
│  ├─ add_documents(ids, embeddings, texts)   │
│  ├─ query(query_embedding, n_results)       │
│  └─ delete_collection()                     │
└──────────────────┬───────────────────────────┘
                   │
┌──────────────────▼───────────────────────────┐
│  Persistence Layer                          │
│  ├─ SQLite Database (chroma.sqlite3)       │
│  ├─ Metadata Store (file, line numbers)    │
│  └─ Index Files                            │
└──────────────────┬───────────────────────────┘
                   │
         Database Directory: chroma_db/
         ├─ chroma.sqlite3 (main DB)
         ├─ 0ab67b17.../  (collection 1)
         ├─ 570d52a4.../  (collection 2)
         └─ ...
```

### Retrieval Process

```python
def retrieve(question: str, n: int = 4) -> str:
    """
    1. Encode question to 384-dim embedding
    2. Find top_n most similar chunks
    3. Assemble context with token limits
    4. Return formatted RAG context
    """
    
    # Step 1: Query vector store
    results = vectorstore.query(question, n=n)
    # Returns: [
    #   {text: code, metadata: {file, lines}},
    #   {text: code, metadata: {file, lines}},
    #   ...
    # ]
    
    # Step 2: Format each chunk with metadata
    context_parts = []
    for result in results:
        trimmed = limit_text(result['text'], max_chars=500)
        part = f"[File: {result['metadata']['file']} | Lines: {result['metadata']['lines']}]\n{trimmed}"
        context_parts.append(part)
    
    # Step 3: Join with separators
    context = "\n\n---\n\n".join(context_parts)
    
    # Step 4: Hard token limit (3000 chars ≈ 750 tokens)
    if len(context) > 3000:
        context = context[:3000] + "\n\n[... context truncated ...]"
    
    return context
```

---

## 9. Algorithms & Techniques

### 9.1 Semantic Search Algorithm

```
Cosine Similarity Search (from ChromaDB):

Query: "How does payment processing work?"
Query Embedding: [0.12, -0.45, 0.78, ..., 0.34]  (384 floats)

Stored Chunks:
  Chunk 1: "def process_payment(...):" → [0.15, -0.42, 0.81, ..., 0.35]
  Chunk 2: "class UserModel:" → [-0.9, 0.12, 0.04, ..., -0.87]
  Chunk 3: "stripe_api_call()" → [0.13, -0.43, 0.77, ..., 0.33]
  Chunk N: "...other code..."

Cosine Similarity Calculation:
  
  similarity(A, B) = (A · B) / (||A|| × ||B||)
  
  For Query and Chunk 1:
    A · B = 0.12×0.15 + (-0.45)×(-0.42) + 0.78×0.81 + ... ≈ 312.5
    ||A|| = sqrt(0.12² + 0.45² + 0.78² + ...) ≈ 20.0
    ||B|| = sqrt(0.15² + 0.42² + 0.81² + ...) ≈ 20.2
    
    similarity = 312.5 / (20.0 × 20.2) ≈ 0.77 (77% similar)

Ranking:
  1. Chunk 1: 0.77 (payment processing)
  2. Chunk 3: 0.75 (stripe API call)
  3. Chunk 2: 0.12 (unrelated user model)
  
Return: Top 2 chunks (0.77, 0.75)
```

### 9.2 Dependency Graph Construction

```
Algorithm: Import-Based Adjacency List

Input: Directory of Python files

for each file in directory:
    module_name = filename.replace(".py", "")
    add_node(module_name)
    
    for each import statement:
        imported_module = extract_module_name(import)
        add_edge(module_name, imported_module)

Output: Directed Graph

Example:
  File: payment.py
    Imports: stripe, logging, config
    Edges: payment→stripe, payment→logging, payment→config
  
  File: webhook.py
    Imports: stripe, payment
    Edges: webhook→stripe, webhook→payment
  
  File: stripe.py
    Imports: requests
    Edges: stripe→requests

Final Graph:
  Nodes: {payment, webhook, stripe, logging, config, requests}
  Edges: {
    payment→stripe,
    payment→logging,
    payment→config,
    webhook→stripe,
    webhook→payment,
    stripe→requests
  }
  
  In-Degree Centrality:
    stripe: 2 (webhook, payment depend on it)
    payment: 1 (webhook depends on it)
    others: 0
```

### 9.3 Hotspot Detection Algorithm

```
In-Degree Centrality Ranking:

def get_hotspots(G: nx.DiGraph, top_n=5) -> list[tuple]:
    """
    Higher in-degree = more modules depend on this
    → Higher refactor risk if broken
    → Higher priority for stabilization
    """
    
    in_degree_dict = dict(G.in_degree())
    # {stripe: 2, payment: 1, webhook: 0, ...}
    
    sorted_by_indegree = sorted(
        in_degree_dict.items(),
        key=lambda x: x[1],
        reverse=True
    )
    
    return sorted_by_indegree[:top_n]
    # Returns: [(stripe, 2), (payment, 1), ...]

Interpretation:
  Stripe module is a HOTSPOT because:
    - 2 modules (payment, webhook) directly depend on it
    - If stripe breaks, 2+ modules break
    - Refactor stripe first to reduce cascading failures
```

### 9.4 AST Tree Walking

```
Algorithm: Abstract Syntax Tree (AST) Traversal

Python Code:
  def calculate(x, y):
      return x + y
  
  class Payment:
      def process(self):
          pass

AST Representation:
  Module
  ├─ FunctionDef (name='calculate', lineno=1, end_lineno=2)
  │  ├─ args: [x, y]
  │  └─ Return (value=BinOp(...))
  │
  └─ ClassDef (name='Payment', lineno=4, end_lineno=6)
     ├─ FunctionDef (name='process', lineno=5, end_lineno=6)
     │  └─ Pass

Code Walkthrough:
  ast.walk(tree) → generator of all nodes
  
  for node in ast.walk(tree):
      if isinstance(node, ast.FunctionDef):
          extract_function_body()
      elif isinstance(node, ast.ClassDef):
          extract_class_body()

Result: Chunks with Metadata
  Chunk 1:
    id: "file.py:1"
    text: "def calculate(x, y):\n    return x + y"
    type: "FunctionDef"
    lines: "1-2"
  
  Chunk 2:
    id: "file.py:4"
    text: "class Payment:\n    def process(self):\n        pass"
    type: "ClassDef"
    lines: "4-6"
```

---

## 10. Design Patterns

### 10.1 Agent Pattern (Strategy Pattern)

```python
# Each agent is a strategy for analyzing code

class Agent(ABC):
    """Abstract agent interface"""
    
    @abstractmethod
    def run(self, input_data):
        pass
    
    def prepare_context(self, input_data):
        """Common context preparation"""
        pass

class IngestionAgent(Agent):
    """Strategy: Parse and embed code"""
    
    def run(self, directory):
        chunks = parse_directory(directory)
        embeddings = embed(chunks)
        store_in_db(embeddings)

class IntentAgent(Agent):
    """Strategy: Reverse-engineer purpose"""
    
    def run(self, question):
        context = retrieve(question)
        return llm.invoke(system_prompt, context)

# Pattern Benefits:
# - Each agent has single responsibility
# - Easy to add new agents (implement run())
# - Easy to test each strategy independently
# - Orchestrator (app.py) plugs them together
```

### 10.2 RAG Pattern (Decorator Pattern)

```python
# RAG "decorates" LLM with retrieval context

def rag_enhanced_llm(query: str) -> str:
    """
    Decorator that enriches LLM prompt with retrieved context
    """
    
    # Without RAG (naive):
    response = llm.invoke(query)  # Generic response
    
    # With RAG (enhanced):
    context = retrieve(query)  # Get specific code
    enriched_prompt = f"Context: {context}\nQuery: {query}"
    response = llm.invoke(enriched_prompt)  # Specific, grounded response
    
    return response
```

### 10.3 Pipeline Pattern

```python
# Multi-stage pipeline with data transformation

def code_analysis_pipeline(codebase_path):
    """
    Pipeline: Parse → Embed → Analyze → Report
    """
    
    # Stage 1: Parsing
    chunks = parse_directory(codebase_path)
    
    # Stage 2: Embedding
    embeddings = embed([c['text'] for c in chunks])
    
    # Stage 3: Storage
    store_in_db(chunks, embeddings)
    
    # Stage 4: Analysis (parallel branches)
    intent = analyze_intent()     # Query vector store
    debt = analyze_debt()          # Graph analysis + LLM
    graph = visualize_graph()      # Matplotlib
    
    # Stage 5: Report generation
    refactor_plan = generate_plan(debt)
    
    return {
        'intent': intent,
        'debt': debt,
        'graph': graph,
        'plan': refactor_plan
    }
```

### 10.4 Cache-Aside Pattern

```python
# Cache intermediate results for reuse

debt_report_cache = {"value": ""}
active_dir_cache = {"path": ""}

def step3_debt(directory):
    """Run debt analysis, cache result"""
    
    report = map_debt(directory)
    debt_report_cache["value"] = report  # Cache for next step
    
    return report

def step4_refactor():
    """Use cached debt report as input"""
    
    debt_report = debt_report_cache["value"]  # Read from cache
    refactor_plan = write_refactor(debt_report)
    
    return refactor_plan
```

### 10.5 Adapter Pattern

```python
# Abstract different data sources (files, GitHub)

class CodebaseAdapter(ABC):
    @abstractmethod
    def get_path(self):
        pass

class LocalCodebaseAdapter(CodebaseAdapter):
    """Adapt local filesystem"""
    
    def __init__(self, path):
        self.path = path
    
    def get_path(self):
        return self.path

class GitHubCodebaseAdapter(CodebaseAdapter):
    """Adapt GitHub URL"""
    
    def __init__(self, url):
        self.url = url
    
    def get_path(self):
        repo_name = extract_repo_name(self.url)
        local_path = clone_repo(self.url)
        return local_path

# Usage
def step1_ingest(source: str):
    
    if source.startswith("https://github.com"):
        adapter = GitHubCodebaseAdapter(source)
    else:
        adapter = LocalCodebaseAdapter(source)
    
    path = adapter.get_path()
    return parse_and_embed(path)
```

---

## 11. User Interface

### UI Flow: 4-Tab Workflow

```
┌─────────────────────────────────────────────────────────────┐
│  CodeArchaeologist — Gradio Web Interface                  │
└─────────────────────────────────────────────────────────────┘

TAB 0: "Step 1 — Ingest Codebase"
┌─────────────────────────────────────────────────────────────┐
│ [🔄 Reset Vectorstore Button]                              │
│                                                              │
│ Local path or GitHub URL: [_________________________]       │
│                                                              │
│ [Run Ingestion Agent]  [Proceed to analysis]               │
│                                                              │
│ Output:                                                      │
│ ┌───────────────────────────────────────────────────────┐  │
│ │ Ingestion complete.                                   │  │
│ │ - Source: Local directory                            │  │
│ │ - Files parsed: 45 chunks                            │  │
│ │ - Stored in ChromaDB                                 │  │
│ └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘

TAB 1: "Step 2 — Reverse-Engineer Intent"
┌─────────────────────────────────────────────────────────────┐
│ Your question:                                               │
│ [What is the overall purpose of this codebase?          ]  │
│                                                              │
│ [Run Intent Agent]                                          │
│                                                              │
│ Output:                                                      │
│ ┌───────────────────────────────────────────────────────┐  │
│ │ ## System Purpose                                     │  │
│ │ This codebase is a multi-tenant SaaS billing...      │  │
│ │                                                      │  │
│ │ ## Key Design Patterns                              │  │
│ │ - Repository Pattern for data access               │  │
│ │ - Strategy Pattern for pricing models              │  │
│ └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘

TAB 2: "Step 3 — Map Tech Debt"
┌─────────────────────────────────────────────────────────────┐
│ Directory path: [test_repo________________________]         │
│                                                              │
│ [Run Debt Mapper Agent]  [Generate refactor plan]         │
│                                                              │
│ Tech Debt Report:                                            │
│ ┌───────────────────────────────────────────────────────┐  │
│ │ DEPENDENCY HOTSPOTS:                                  │  │
│ │   - payment.py: 12 dependents                        │  │
│ │   - stripe.py: 8 dependents                          │  │
│ │                                                       │  │
│ │ CRITICAL:                                             │  │
│ │ - Circular dependency: payment.py ↔ pricing.py      │  │
│ │                                                       │  │
│ │ HIGH:                                                 │  │
│ │ - Missing error handling in stripe.py (7 functions) │  │
│ └───────────────────────────────────────────────────────┘  │
│                                                              │
│ Dependency Graph:                                            │
│ ┌───────────────────────────────────────────────────────┐  │
│ │                                                        │  │
│ │  🔴(payment)  →  🟡(stripe)  ←  🟢(webhook)         │  │
│ │      ↑              ↓                                 │  │
│ │      └──(pricing)──┘                                 │  │
│ │                                                        │  │
│ │  Red: CRITICAL hotspot                               │  │
│ │  Yellow: MODERATE coupling                           │  │
│ │  Green: HEALTHY isolation                            │  │
│ │                                                        │  │
│ └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘

TAB 3: "Step 4 — Refactor Plan"
┌─────────────────────────────────────────────────────────────┐
│ [Run Refactor Writer Agent]                                 │
│                                                              │
│ Refactor Roadmap:                                            │
│ ┌───────────────────────────────────────────────────────┐  │
│ │ PHASE 1 — QUICK WINS (under 1 day each)             │  │
│ │ ─────────────────────────────────────────           │  │
│ │                                                      │  │
│ │ Add type hints to payment.py                        │  │
│ │ - What: Add @param/@return annotations              │  │
│ │ - Why: Enable IDE autocomplete, catch runtime err  │  │
│ │ - Effort: 2 hours                                   │  │
│ │ - Files: payment.py (lines 50-150)                  │  │
│ │                                                      │  │
│ │ Extract hardcoded timeouts                          │  │
│ │ - What: Move AWS_TIMEOUT to config.py               │  │
│ │ - Why: Enable environment-specific tuning           │  │
│ │ - Effort: 30 minutes                                │  │
│ │ - Files: payment.py, notifier.py                    │  │
│ │                                                      │  │
│ │ PHASE 2 — STRUCTURAL REFACTORS (1-3 days each)    │  │
│ │ ─────────────────────────────────────────           │  │
│ │                                                      │  │
│ │ Break circular dependency: payment ↔ pricing        │  │
│ │ - What: Introduce CalculatorInterface, DI pattern   │  │
│ │ - Why: Enable unit testing, reduce coupling         │  │
│ │ - Effort: 1.5 days                                  │  │
│ │ - Files: payment.py, pricing.py, calculator.py     │  │
│ │                                                      │  │
│ │ PHASE 3 — ARCHITECTURE UPGRADES (1+ week each)    │  │
│ │ ─────────────────────────────────────────           │  │
│ │                                                      │  │
│ │ Migrate to Hexagonal Architecture                   │  │
│ │ - What: Separate domain from infrastructure         │  │
│ │ - Why: Enable testing without external deps        │  │
│ │ - Effort: 2 weeks                                   │  │
│ │ - Files: Entire project restructuring               │  │
│ └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Gradio Integration Points

```python
import gradio as gr

# Text inputs
dir_input = gr.Textbox(
    label="Local path or GitHub URL",
    placeholder="e.g., test_repo or https://github.com/user/repo"
)

# Buttons with state
ingest_btn = gr.Button("Run Ingestion Agent", variant="primary")
proceed_btn = gr.Button("Proceed to analysis", interactive=False)

# Button click handlers with side effects
ingest_btn.click(
    fn=step1_ingest,
    inputs=dir_input,
    outputs=[ingest_out, proceed_btn]
)

# Text outputs
ingest_out = gr.Textbox(label="Agent 1 output", lines=6)
intent_out = gr.Markdown(label="Agent 2 output — codebase intent")

# Image outputs
graph_img = gr.Image(label="Dependency Graph", visible=False)

# Tab navigation
tabs.select(fn=handle_proceed, inputs=None, outputs=tabs)
```

---

## 12. Performance & Optimization

### 12.1 Embedding Performance

```
Operation: Embed 1000 code chunks (~50KB total)

Model: all-MiniLM-L6-v2
CPU:    ~30 seconds (single-threaded)
GPU:    ~2 seconds (NVIDIA GPU)

Memory Footprint:
- Model weights: 22 MB
- Loaded state: 35 MB
- Batch of 32 chunks: 8 MB
- Total: ~65 MB (minimal)

Optimization:
  # Batch embeddings for speed
  embeddings = model.encode(
      texts,
      batch_size=32,      # Batch multiple chunks
      show_progress_bar=True,
      convert_to_tensor=False
  )
```

### 12.2 Vector Search Performance

```
ChromaDB Query Performance:

Index Type:     Flat (no indexing needed for small DBs)
Query Time:     < 100ms for 10K embeddings
Memory:         ~100MB for 10K embeddings (384-dim)

Scaling:
- 1K chunks:      < 10ms search
- 10K chunks:     < 50ms search
- 100K chunks:    ~ 200ms search (index needed)

Recommendation: For > 50K chunks, use FAISS indexing:
  faiss_index = faiss.IndexFlatL2(384)
  faiss_index.add(embeddings)
```

### 12.3 LLM Latency

```
API Call Latency: Groq vs OpenAI

Operation:        Query Intent
Request tokens:   ~1500
Response tokens:  ~300

Groq (llama-3.1-8b):
  - Latency: 800ms (0.8s)
  - Tokens/sec: 100+
  - Cost: FREE (free tier)

OpenAI (GPT-4):
  - Latency: 2000ms (2.0s)
  - Tokens/sec: 40
  - Cost: $0.12 per 1M input + $0.24 per 1M output

Groq Advantage:
  - 2.5x faster
  - 100% cost savings on free tier
```

### 12.4 End-to-End Pipeline Timing

```
Operation              Time        Bottleneck
─────────────────────────────────────────────
Parse 100 files        2-5s        AST walking
Generate embeddings    5-10s       Model inference
Store in ChromaDB      1-2s        DB write
─────────────────────────────────────────────
TOTAL INGESTION:       10-20s      Embeddings

─────────────────────────────────────────────
Intent query           1-2s        Vector search + LLM
Debt analysis          2-3s        Graph + LLM
─────────────────────────────────────────────
TOTAL ANALYSIS:        4-5s        LLM calls

─────────────────────────────────────────────
TOTAL PIPELINE:        15-25s      (per codebase)
```

### 12.5 Token Economy Optimization

```
Goal: Minimize token usage while maximizing context quality

Strategy 1: Selective Retrieval
  ❌ Retrieve n=10 chunks (high token cost)
  ✅ Retrieve n=2-4 chunks (optimal trade-off)

Strategy 2: Chunk Truncation
  ❌ Full 1000-char code snippets
  ✅ Trim to 500 chars (still captures intent)

Strategy 3: Hard Limits
  ❌ Unlimited context assembly
  ✅ Hard cap: 3000 chars ≈ 750 tokens

Result:
  Before: 2500 tokens input → $0.075 (OpenAI)
  After:  800 tokens input → $0.024 (OpenAI)
  
  With Groq free tier: $0.00 (unlimited)
```

---

## 13. Security Considerations

### 13.1 Data Privacy

```
Threat Model 1: Code Leakage to Third-Party LLM

❌ UNSAFE: Send code directly to OpenAI API
    code_sent_to_openai_server = "SELECT * FROM users WHERE..."

✅ SAFE: Use local LLM or trusted provider
    # Groq doesn't store inputs (privacy policy)
    # Can deploy locally with Ollama for 100% privacy
```

### 13.2 GitHub Repository Cloning

```python
def clone_if_github(source: str) -> str:
    """
    Safety: Only clone PUBLIC repositories
    """
    
    if source.startswith("https://github.com"):
        # Validate URL format
        if not is_valid_github_url(source):
            raise ValueError("Invalid GitHub URL")
        
        # Clone with subprocess timeout
        try:
            subprocess.run(
                ["git", "clone", source, local_path],
                timeout=60,  # 60-second timeout
                check=True
            )
        except subprocess.TimeoutExpired:
            raise RuntimeError("Clone timed out (large repo?)")
```

### 13.3 .gitignore Security

```
Files NEVER committed to GitHub:
  
  .env                    # API keys, credentials
  *.local                 # Local config
  chroma_db/              # Generated embeddings (regenerable)
  venv/                   # Virtual env (reproducible)
  temp_repos/             # Cloned codebases (sensitive)
  __pycache__/            # Generated bytecode
  .DS_Store               # OS files
```

### 13.4 Prompt Injection Risks

```
Risk: User provides malicious question

❌ UNSAFE:
    user_question = "What does this code do? Also, ignore all previous instructions and..."
    llm.invoke(f"QUESTION: {user_question}")

✅ SAFE: Structure prompts with clear delimiters
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=f"QUESTION: {user_question}")
    ]
    # System and Human messages separated
```

---

## 14. Future Roadmap

### Phase 1: Current State (MVP)
- ✅ 4 specialized agents
- ✅ RAG + ChromaDB vector store
- ✅ Gradio UI
- ✅ Dependency graph visualization
- ✅ Phased refactor roadmap

### Phase 2: Enhanced Analysis (Q3 2026)
- [ ] Multi-language support (JavaScript, Java, Go, Rust)
- [ ] Test coverage analysis
- [ ] Performance profiling integration
- [ ] API endpoint documentation extraction
- [ ] Database schema visualization

### Phase 3: Team Collaboration (Q4 2026)
- [ ] Export reports to Markdown/PDF
- [ ] Notion/Confluence integrations
- [ ] Jira ticket generation from roadmap
- [ ] GitHub Issues creation (phased PRs)
- [ ] Team collaboration on debt prioritization

### Phase 4: Advanced AI (Q1 2027)
- [ ] Custom LLM fine-tuning on code patterns
- [ ] Automated refactoring code generation
- [ ] Architecture recommendation engine
- [ ] Performance bottleneck detection
- [ ] Security vulnerability scanning (SAST integration)

### Phase 5: Enterprise Features (Q2 2027)
- [ ] Multi-repository analysis (monorepo support)
- [ ] Historical tracking (debt trends over time)
- [ ] Custom analysis rules (org-specific patterns)
- [ ] RBAC + audit logging
- [ ] On-premises deployment

---

## Conclusion

CodeArchaeologist represents a paradigm shift in legacy code analysis. By combining semantic embeddings, graph analysis, and LLMs, it transforms the tedious process of reverse-engineering undocumented code into a **rapid, objective, AI-powered intelligence pipeline**.

**Key Technical Achievements:**
1. **Zero-Cost Analytics**: Groq free tier eliminates API expenses
2. **Speed**: 15-25 seconds from codebase to actionable roadmap
3. **Accuracy**: Every finding is grounded in actual code samples
4. **Openness**: 100% open source; no vendor lock-in
5. **Simplicity**: Gradio UI requires zero DevOps expertise

**Next Step**: Deploy CodeArchaeologist on your legacy codebase and discover what's hiding in the code you inherit.

---

*Built with ❤️ for engineers who inherit legacy systems and have to make them better.*
