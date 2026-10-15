# ═══════════════════════════════════════════════════════════════════════
# SYS_01 // AGENTIC GRAPHRAG ENGINE JUSTFILE
# Frontend: Vite + React 19 + TypeScript (Bun)
# Backend:  FastAPI + LangGraph + ColBERTv2 + Neo4j (Python uv)
# ═══════════════════════════════════════════════════════════════════════

# Default recipe: list all available commands
default:
    @just --list

# Install all dependencies for both backend (uv) and frontend (bun)
install:
    @echo "[+] Syncing Python backend dependencies with uv..."
    uv sync --extra dev
    @echo "[+] Installing React frontend dependencies with bun..."
    cd frontend && bun install

# Run backend independently on port 8001
backend host="0.0.0.0" port="8001":
    @echo "[*] Launching Agentic GraphRAG FastAPI backend on http://{{host}}:{{port}}..."
    uv run uvicorn src.main:app --host {{host}} --port {{port}} --reload

# Run frontend independently on port 5171 (proxies /api to backend)
frontend:
    @echo "[*] Launching Vite React frontend on http://localhost:5171..."
    cd frontend && bun run dev

# Run both backend and frontend concurrently (requires backgrounding or separate terminals)
dev:
    @echo "[*] Launching Agentic GraphRAG Mesh (Backend: :8001 | Frontend: :5171)..."
    @echo "Tip: Run 'just backend' and 'just frontend' in separate terminals for independent logs."
    (trap 'kill 0' SIGINT; just backend & just frontend)

# Build production bundle for the frontend
build:
    @echo "[*] Building React frontend production bundle..."
    cd frontend && bun run build

# Run all test suites across backend and frontend
test:
    @echo "[*] Running backend pytest suite..."
    uv run pytest
    @echo "[*] Typechecking frontend..."
    cd frontend && bun run build

# Execute CLI multi-agent investigation query
query q="Assess single-point supply chain vulnerabilities across leading semiconductor clients." tickers="AAPL NVDA":
    uv run graphrag query -q "{{q}}" -t {{tickers}}

# Inspect knowledge graph multi-hop relationships via CLI
graph ticker="AAPL" depth="2":
    uv run graphrag graph -t {{ticker}} -d {{depth}}

# Benchmark retrieval and reasoning latency SLA
benchmark n="5":
    uv run graphrag benchmark -n {{n}}

# Build container image with multi-stage Bun + uv
docker-build:
    docker build -t agentic-graphrag-engine:latest .

# Launch all infrastructure services (API, Neo4j, Qdrant, Redis)
docker-up:
    docker compose up -d

# Stop infrastructure services
docker-down:
    docker compose down
