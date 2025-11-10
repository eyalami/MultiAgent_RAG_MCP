                                ┌──────────────────────────┐
                                │        User / UI         │
                                │ (Swagger UI / Frontend)  │
                                └────────────┬─────────────┘
                                             │  REST POST /chat
                                             ▼
                                ┌──────────────────────────┐
                                │     FastAPI Backend      │
                                │  (Chat endpoint handler) │
                                └────────────┬─────────────┘
                                             │
                                             ▼
                                ┌──────────────────────────┐
                                │     ManagerAgent         │
                                │ (Graph Orchestrator)     │
                                └────────────┬─────────────┘
                                             │
             ┌───────────────────────────────┴──────────────────────────────┐
             │                                                              │
             ▼                                                              ▼
  ┌──────────────────────────┐                                  ┌──────────────────────────┐
  │        KBAgent           │                                  │        MCPAgent          │
  │ (Knowledge Base Search)  │                                  │ (Summarize via Subgraph) │
  └────────────┬─────────────┘                                  └────────────┬─────────────┘
               │                                                              │
               │                                                              │
               ▼                                                              ▼
  ┌──────────────────────────┐                                  ┌──────────────────────────┐
  │   In-Memory FAISS Index  │                                  │      MCP Subgraph        │
  │  (Prebuilt embeddings)   │                                  │ ┌──────────────────────┐ │
  │  Built at Docker build   │                                  │ │   (a) MCP Client     │ │
  │  time for simplicity     │                                  │ │   Calls Tavily API   │ │
  │  (Top-K vector search)   │                                  │ │   → Fetch articles   │ │
  └──────────────────────────┘                                  │ └──────────────────────┘ │
                                                                 │ ┌──────────────────────┐ │
                                                                 │ │   (b) LLM Summarizer │ │
                                                                 │ │   Summarizes content │ │
                                                                 │ └──────────────────────┘ │
                                                                 └────────────┬─────────────┘
                                                                              │
                                                                              ▼
                                                             ┌──────────────────────────┐
                                                             │ Summarized Articles JSON │
                                                             │ or List[str]             │
                                                             └────────────┬─────────────┘
                                                                              │
                                                                              ▼
                                ┌──────────────────────────┐
                                │     ManagerAgent         │
                                │   (Unifies results)      │
                                │   Formats output text    │
                                └────────────┬─────────────┘
                                             │
                                             ▼
                                ┌──────────────────────────┐
                                │  FastAPI Response (JSON) │
                                │   Formatted summaries    │
                                │   with numbered sources  │
                                └────────────┬─────────────┘
                                             │
                                             ▼
                                ┌──────────────────────────┐
                                │        User / UI         │
                                │  Receives readable text  │
                                └──────────────────────────┘


Key Notes
	•	Flow order:
            FastAPI /chat → ManagerAgent → KBAgent → MCPAgent (→ MCP Client + LLM) → back to ManagerAgent → response
	•	FAISS index:
            Prebuilt at Docker build time from cached embeddings for fast lookups; not rebuilt per request.
	•	MCPAgent subgraph:
            Combines remote content fetching (Tavily HTTP MCP) and summarization (LLM).
	•	Production plan:
            FAISS embedding refresh would run as a separate cron-triggered or manual job, decoupled from request flow.
    •	Error Handling:
            I didn't implement error handling, retries, timeouts, fallback etc. at graph level. I have selected langgraph because it supports all of the above easily through node decorators, error handling states etc. At production level I would implement these. 
