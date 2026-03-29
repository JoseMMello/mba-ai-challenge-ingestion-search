#!/usr/bin/env sh
set -e

if [ "${AUTO_INGEST_ON_START:-true}" = "true" ]; then
  echo "[api-entrypoint] Iniciando indexação do PDF..."
  python src/ingest.py
  echo "[api-entrypoint] Indexação concluída."
else
  echo "[api-entrypoint] AUTO_INGEST_ON_START=false, pulando indexação."
fi

exec "$@"
