# 🔍 CodeArchaeologist

**Reverse-engineer any legacy codebase in hours, not weeks.** CodeArchaeologist is a multi-agent AI system that automatically analyzes undocumented code, maps technical debt, and generates a structured phased refactoring roadmap your team can execute immediately.

---

## 📖 The Novel: Why CodeArchaeologist Exists

### The Problem: Legacy Code Paralysis

Every organization faces the same nightmare: a critical system that nobody fully understands. The original architects have moved on. Documentation is outdated or non-existent. The codebase is a maze of god objects, circular dependencies, hardcoded values, and mysterious business logic. When something breaks, you're flying blind. When you need to refactor, you don't know where to start.

Modern teams spend weeks or months reverse-engineering legacy systems just to understand what they do—time that could be spent actually improving them. The cost isn't just technical; it's psychological. Developers lose confidence in the code they inherit.

### The Solution: AI-Powered Code Archaeology

CodeArchaeologist treats legacy code like an archaeological dig. Just as archaeologists carefully excavate, catalog, and interpret artifacts to understand ancient civilizations, CodeArchaeologist methodically:

1. **Excavates** the codebase, extracting every function, class, and module
2. **Catalogs** them into a searchable semantic index (using embeddings)
3. **Interprets** their purpose, dependencies, and design patterns
4. **Maps** the technical debt hidden within
5. **Generates** an actionable refactoring roadmap

The system deploys four AI agents that work in concert—each a specialist with a singular focus. They don't just report problems; they synthesize intelligence and recommend next steps organized by effort and impact.

### The Promise

With CodeArchaeologist, your team gains:
- **Clarity**: Understand what your system does in hours, not weeks
- **Confidence**: Know the dependencies, hotspots, and debt
- **Direction**: A prioritized refactoring plan your team can execute
- **Control**: Open source, runs locally, no vendor lock-in

---

## 🏗️ How It Works

CodeArchaeologist deploys four specialized agents that work together to transform code chaos into actionable engineering intelligence:

| Agent | Role | Key Technology |
|-------|------|---|
| **Ingestion Agent** | Chunks codebase, builds embeddings, indexes into vector database | tree-sitter + ChromaDB + sentence-transformers |
| **Intent Reverse-Engineer** | Identifies system purpose, design patterns, business logic, data flows | LangChain + Groq LLM + RAG retrieval |
| **Tech Debt Mapper** | Detects god modules, missing error handling, circular deps, hardcoded config | NetworkX dependency analysis + pattern detection |
| **Refactor Plan Writer** | Outputs phased roadmap: quick wins, structural fixes, architecture upgrades | LangChain prompt engineering |

---

## 🎯 Architecture Overview

CodeArchaeologist follows a retrieval-augmented generation (RAG) pipeline optimized for code analysis:

### The Pipeline

```
Your Codebase
    ↓
[Ingestion Agent] → Parse with tree-sitter → Extract functions/classes
    ↓
[AST Parser] → Generate semantic chunks
    ↓
[Embeddings] → Convert chunks to vectors (sentence-transformers)
    ↓
[ChromaDB] → Store and index vectors for rapid retrieval
    ↓
[Dependency Graph] → Build NetworkX graph of imports/calls
    ↓
[Intent Agent] + [Debt Agent] → Query vector store, retrieve context, feed to LLM
    ↓
[Refactor Agent] → Synthesize reports into phased roadmap
    ↓
[Gradio UI] → Display results, download reports
```

### Key Insights

- **Parsing**: tree-sitter parses code incrementally, capturing functions and classes with precise line numbers
- **Embeddings**: sentence-transformers creates dense semantic vectors from code chunks, enabling similarity search
- **Vector Store**: ChromaDB indexes embeddings, allowing RAG queries to find relevant code snippets in milliseconds
- **Dependency Analysis**: NetworkX builds a directed graph of module dependencies to identify hotspot modules (high in-degree centrality)
- **LLM Integration**: LangChain chains prompts with Groq's fast LLM API to synthesize findings into reports
- **Phased Recommendations**: Refactorings are categorized as:
  - **Quick Wins**: Under 1 day
  - **Structural Fixes**: 1-3 days
  - **Architecture Upgrades**: 1+ weeks

The entire system is orchestrated via **Gradio**, providing a web interface for uploading codebases, monitoring progress, and downloading structured reports.

---

## 🚀 Open Source Stack

- **Code Parsing**: tree-sitter (incremental parsing for Python, JavaScript, more)
- **Embeddings**: sentence-transformers (HuggingFace community models)
- **Vector Database**: ChromaDB (lightweight, SQLite-backed)
- **Dependency Analysis**: NetworkX (graph algorithms)
- **LLM Framework**: LangChain (orchestration layer)
- **LLM Provider**: Groq (free tier, 9000+ requests/day)
- **Visualization**: Matplotlib (graphs and charts)
- **UI**: Gradio (zero-config web interface)
- **PDF Extraction**: PyMuPDF (document parsing)

✅ **Zero licensing costs**. All dependencies are open source or have free tiers.

---

## ⚡ Quick Start

### 1. Clone and Setup Virtual Environment

```bash
git clone https://github.com/Vishnuvaradhan-M/code-archaeologist.git
cd code-archaeologist
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

Create a `.env` file in the project root:

```
GROQ_API_KEY=your_groq_api_key_here
CODEBASE_PATH=/path/to/legacy/codebase
OUTPUT_DIR=./reports
```

Get a free Groq API key at [console.groq.com](https://console.groq.com).

### 4. Run the Application

```bash
python app.py
```

The Gradio interface will start at `http://localhost:7860`. Upload a codebase directory and watch as the agents analyze it in real time.

## Example Outputs

### Intent Reverse-Engineer Report

```
SYSTEM PURPOSE
This codebase implements a multi-tenant SaaS billing platform.
Core responsibility: Calculate metered usage, apply pricing rules, generate invoices.

DESIGN PATTERNS IDENTIFIED
- Repository Pattern: Data access isolated in db/ module
- Strategy Pattern: Pricing rules via pluggable calculator classes
- Observer Pattern: Webhook notifications on billing events
- Facade Pattern: BillingService shields consumers from 12+ internal dependencies

BUSINESS PROBLEM SOLVED
Enables subscription businesses to meter usage (API calls, storage, compute) 
and charge customers with 100+ distinct pricing models without rebuilding 
billing logic for each customer.

DATA FLOW
[Customer usage events] → [Aggregation service] → [Pricing engine] → 
[Invoice generator] → [Webhook notifier]
```

### Tech Debt Mapper Report

```
EXECUTIVE SUMMARY
104 debt items identified across 23 modules
- 3 CRITICAL severity
- 17 HIGH severity
- 34 MEDIUM severity
- 50 LOW severity

CRITICAL FINDINGS
1. BillingService (billing.py): Circular dependency with PricingEngine
   Risk: Blocks refactoring, breaks testability
   
2. InvoiceGenerator (invoicing.py): 7 hardcoded AWS timeouts
   Risk: Fails in low-latency environments, environment-specific bugs

HOTSPOT ANALYSIS
Module 'pricing.py' has 23 inbound imports (highest in graph)
Contains: Missing error handling on 4 calculation methods
         No type hints on 8 functions
         Deeply nested logic (max depth: 7)
```

### Refactor Plan Writer Report

```
PHASE 1: Quick Wins (2 days total)
- Add type hints to BillingService (4 hours) → improves IDE support, enables type checking
- Extract hardcoded timeouts to config.py (2 hours) → enables environment-specific tuning
- Replace 23 print statements with structured logging (3 hours) → improves debugging

PHASE 2: Structural Refactors (5 days)
- Break circular dependency via Dependency Injection (3 days) → enables unit testing
- Extract Pricing Strategy classes (2 days) → reduces god class responsibility by 40%

PHASE 3: Architecture Upgrade (2 weeks)
- Introduce Repository pattern for all data access (1 week) → enables database swapping
- Refactor to hexagonal architecture (1 week) → decouples domain from infrastructure
```

## Why This Matters

**For Enterprise Engineering Teams:**

Legacy codebases are business assets—they generate revenue, serve customers, and contain hard-won domain knowledge. But they're invisible. New engineers spend weeks understanding them. Technical leaders spend months assessing refactoring feasibility. Debt compounds silently until the system becomes unmaintainable.

CodeArchaeologist solves this in hours:

- **Acceleration**: Onboard engineers to legacy codebases 10x faster with actionable analysis, not fragmented documentation
- **Risk Reduction**: Identify critical technical debt before it becomes an emergency incident
- **Objective Prioritization**: Dependency graphs and severity metrics replace subjective engineering judgment with evidence-based decisions
- **Execution Confidence**: Phased roadmaps let teams refactor without halting feature delivery
- **Knowledge Preservation**: Reverse-engineered intent becomes institutional memory, surviving team turnover

Technical leaders can run CodeArchaeologist on any codebase in hours, generate a refactoring roadmap, and make informed decisions about investment with concrete data.

---

**Built with ❤️ for engineers who inherit legacy systems and have to make them better.**
