# MultiAgent RAG MCP

This repository hosts an experimental multi-agent Retrieval-Augmented Generation (RAG) system that coordinates FastAPI services with Model Context Protocol (MCP) tooling. It preprocesses a local knowledge base, spins up an MCP Client, and serves a chat API that delegates jobs to multiple agents.

## Prerequisites

- A Tavily API key (`TAVILY_API_KEY`) with access to the MCP Tavily proxy
- OPENAI API Key

## Local Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/<your-org>/MultiAgent_RAG_MCP.git
   cd MultiAgent_RAG_MCP
   ```

2. **Copy .env.exampe to .envt**
   ```bash
   copy .env.example .env  
   ```
   Required: edit .env setting your own API KEYS
   Optional: set other parameters e.g. MAX_CHARACTERS

## Running the Stack
## Docker Compose 

1. **Build the image**
   ```bash
   docker compose build
   ```

2. **Run the containers**
   ```bash
   docker compose up -d
   ```

The container downloads the embedding model during the build stage and exposes the FastAPI service on port `80` (mapped above to `8000` on the host).
The first build may take a long time (and even fail) depending on your machine resources

## Project Structure

- `src/agents/`: Multi-agent orchestration logic (`manager_agent`, `kb_agent`, `mcp_agent`)
- `src/api/`: FastAPI routes and request/response schemas
- `data/`: folder hosting the knowledge base and cached embeddings
- `Dockerfile` / `docker-compose.yml`: Containerization and orchestration setup

## Troubleshooting

- **Missing model files** – Delete `data/cache/` and rerun preprocessing to refresh embeddings.
- **MCP proxy fails to connect** – Confirm `TAVILY_API_KEY` is valid and that port `4000` is free.
- **Permission denied on port 80** – Run the server on a higher port or execute the script with elevated privileges.
- **First build fails or takes long time** – set docker resources, allocate more