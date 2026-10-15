# ==============================================================================
# AGENTS.MD — AGENTIC GRAPHRAG ENGINE (SYS_01)
# Production Architecture, Rules & Operational Directives
# Author: Bernard Birendra Das (https://github.com/bernardbdas)
# ==============================================================================

> **MANDATORY SPECIFICATION FOR AUTONOMOUS AGENTS AND DEVELOPERS**
> This repository strictly adheres to the engineering standards, architecture, and design styles specified herein. No simplifications, removals, or degradations are permitted.

---

## 1. System Topology & Identity

- **System ID**: `SYS_01`
- **Repository Name**: `agentic-graphrag-engine`
- **Primary Domain**: Hybrid Agentic Graph-Augmented RAG Engine for SEC 10-K/10-Q Financial Intelligence
- **Backend Port**: `8001` (FastAPI)
- **Frontend Framework**: Vite + React 19 + TypeScript (Scaffolded with `bun`)
- **Frontend Port (Dev)**: `5173`
- **UI Aesthetic Style**: **Cyber-Brutalist Financial Terminal** (Inspired by Bernard's portfolio `bernardbdas.github.io` & UXPlanet Brutalism)
  - Color Palette: Pure `#050505` black base, emerald/toxic green `#22c55e` primary accent, cyan `#00f0ff` highlights, hairline borders `#1f2937`
  - Typography: Monospace (`JetBrains Mono`, `IBM Plex Mono`)
  - Layout: High-density dual-column financial terminal with live supply-chain graph viewer, thought trace timeline, and real-time hallucination auditor
- **Domain CLI**: `graphrag` (`src/cli.py`)

---

## 2. Decoupled Architecture & Execution Directives

1. **Decoupled Independence**:
   - Backend and frontend are completely decoupled and must run independently.
   - Run backend independently: `just backend` (FastAPI on port `8001`).
   - Run frontend independently: `just frontend` (Vite dev server on port `5173`).
   - Run both concurrently: `just dev`.
2. **Production Serving**:
   - Compiling frontend via `just build` writes to `frontend/dist`.
   - In production, FastAPI statically mounts `frontend/dist` at `/`.
   - API endpoints (`/health`, `/metrics`, `/query`, `/graph`, `/search`) always take routing priority.

---

## 3. Project Management with `uv`

1. **UV Enforcement**: All Python environment management, locking, and execution MUST use `uv`. Never invoke global `pip` or `venv`.
2. **Build System**: Managed via `hatchling` in `pyproject.toml`:
   ```toml
   [build-system]
   requires = ["hatchling"]
   build-backend = "hatchling.build"

   [tool.hatch.build.targets.wheel]
   packages = ["src"]
   ```
3. **Dependencies**:
   - Production: `fastapi`, `uvicorn`, `langgraph`, `neo4j`, `qdrant-client`, `ragatouille`, `pydantic`, `click`, `rich`.
   - Development: `pytest`, `pytest-asyncio`, `pytest-cov`, `ruff`, `mypy`, `pre-commit`.

---

## 4. Frontend & UI Design Rules (`bun` & Brutalism)

1. Managed exclusively using `bun` inside `frontend/`.
2. High-contrast cyber-brutalist styling:
   - Monospace font stack with crisp typography.
   - 1px hairline borders without rounded cards or soft blur shadows.
   - Real-time interactive SEC filing entity synthesis, interactive verification reports, and graph visualizers.

---

## 5. Command Runner (`just`) Specification

Standardized `Justfile` tasks:
- `just backend`: Run FastAPI server (`http://localhost:8001`) with reload.
- `just frontend`: Run Bun frontend dev server.
- `just dev`: Launch backend and frontend concurrently.
- `just install`: Install backend with `uv sync --extra dev` and frontend with `bun install`.
- `just test`: Run `uv run pytest` and frontend TypeScript check.
- `just build`: Compile frontend to `dist/` and build Python wheel.
- `just check`: Run `uv run ruff check src` and format checks.
- `just query "<text>"`: Execute multi-agent financial synthesis via CLI.
- `just docker-build`: Build multi-stage production Docker image.
- `just docker-up`: Start Qdrant, Neo4j, Redis, and GraphRAG engine via Docker Compose.

---

## 6. Containerization & Docker

- Multi-stage `Dockerfile`:
  - Stage 1: `oven/bun:1-alpine` compiles `frontend/dist`.
  - Stage 2: `python:3.11-slim` installs dependencies via `uv sync --frozen --no-dev` and hosts FastAPI.
- `docker-compose.yml`: Spins up `agentic-graphrag-engine`, `neo4j` (bolt: 7687, http: 7474), `qdrant` (6333), and `redis` (6379).

---

## 7. Developer Tooling & `.vscode` Setup

- `.vscode/settings.json`: Configured with Ruff default formatter, format on save, and `.venv` python interpreter path.
- `.vscode/launch.json`: Debugging configurations for FastAPI backend, CLI commands, and Chrome frontend.
- `.vscode/extensions.json`: Recommended VS Code extensions.
- `.vscode/tasks.json`: Standard VS Code build and test tasks wired to `just`.

---

## 8. Environment Management Rules

- `example.env`: Tracked template with descriptions for Neo4j, Qdrant, Redis, and LLM endpoints.
- `local.env`: Tracked developer defaults for immediate out-of-the-box local execution.
- `.env` / `.env.local`: Ignored in `.gitignore` for private production credentials.

---

## 9. Code Quality, Linters & Pre-Commit Hooks

- Linter & Formatter: `ruff` with `select = ["E", "F", "I"]`, `line-length = 100`.
- Pre-commit hooks (`.pre-commit-config.yaml`):
  - `trailing-whitespace`, `end-of-file-fixer`, `check-yaml`, `check-toml`, `check-added-large-files` (`--maxkb=5000`), `ruff`, and `ruff-format`.
- All git commits must be verified against pre-commit hooks.

---

## 10. Continuous Integration (CI)

- `.github/workflows/ci.yml` runs on every push and PR to `main`:
  - Python lint (`ruff check src`) and test (`pytest`).
  - Bun frontend typecheck (`tsc -b`) and build (`bun run build`).

---

## 11. Git & Remote Repository Rules

- Branch: `main`.
- Remote: `https://github.com/bernardbdas/agentic-graphrag-engine.git`.
