# MBA IA Challenge - Ingestion + Search (RAG)

## Project structure

- `backend/`: FastAPI API, PDF ingestion, and RAG logic.
- `frontend/`: React interface with streaming responses.
- `docker-compose.yml`: starts database, API, and frontend.

## Requirements

- Docker
- Docker Compose

## 1) Clone and configure environment

```bash
git clone <REPOSITORY_URL>
cd mba-ia-challenge-ingestion-search
cp .env.example .env
```

Optional for local development without Docker (Python):

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
```

Edit `.env` and configure at least:

- `OPENAI_API_KEY` = your key (do not commit it)
- `OPENAI_CHAT_MODEL` = chat model (example: `gpt-4o-mini`)
- `OPENAI_EMBEDDING_MODEL` = embedding model (example: `text-embedding-3-small`)

Optional/important:

- `AUTO_INGEST_ON_START='true'` to run ingestion automatically when the API starts.
- `DATABASE_URL_INTERNAL` is already set for Docker and usually does not need changes.

## 2) Start services

```bash
docker compose up --build -d
```

Services:

- Frontend: `http://localhost:5173`
- API: `http://localhost:8000`
- Postgres (pgvector): `localhost:5432`

## 3) View logs

```bash
docker compose logs -f
```

## 4) Manual ingestion (optional)

Use this when `AUTO_INGEST_ON_START='false'` or when you want to reindex manually:

```bash
docker compose run --rm api python src/ingest.py
```

## 5) Stop services

```bash
docker compose down
```

## Security

- Do not commit `.env`.
- Do not expose `OPENAI_API_KEY` in README, code, issue, or commit.
