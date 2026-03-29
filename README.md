# MBA IA Challenge - Ingestion + Search (RAG)

## Estrutura do projeto

- `backend/`: API FastAPI, ingestao do PDF e RAG.
- `frontend/`: interface React com streaming da resposta.
- `docker-compose.yml`: sobe banco, API e frontend.

## Pre-requisitos

- Docker
- Docker Compose

## 1) Clonar e configurar ambiente

```bash
git clone <URL_DO_REPOSITORIO>
cd mba-ia-challenge-ingestion-search
cp .env.example .env
```

Opcional para desenvolvimento local sem Docker (Python):

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
```

Edite o arquivo `.env` e configure no minimo:

- `OPENAI_API_KEY` = sua chave (nao versionar)
- `OPENAI_CHAT_MODEL` = modelo de chat (ex.: `gpt-4o-mini`)
- `OPENAI_EMBEDDING_MODEL` = modelo de embedding (ex.: `text-embedding-3-small`)

Opcional/importante:

- `AUTO_INGEST_ON_START='true'` para indexar automaticamente ao subir a API.
- `DATABASE_URL_INTERNAL` ja vem configurada para Docker e nao precisa mudar no fluxo padrao.

## 2) Subir os servicos

```bash
docker compose up --build -d
```

Servicos:

- Frontend: `http://localhost:5173`
- API: `http://localhost:8000`
- Postgres (pgvector): `localhost:5432`

## 3) Ver logs

```bash
docker compose logs -f
```

## 4) Ingestao manual (opcional)

Use quando `AUTO_INGEST_ON_START='false'` ou quando quiser reindexar manualmente:

```bash
docker compose run --rm api python src/ingest.py
```

## 5) Parar os servicos

```bash
docker compose down
```

## Seguranca

- Nao commitar `.env`.
- Nao publicar `OPENAI_API_KEY` em README, codigo, issue ou commit.
