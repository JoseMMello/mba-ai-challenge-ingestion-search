FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src ./src
COPY docker ./docker
COPY document.pdf ./document.pdf

EXPOSE 8000

ENTRYPOINT ["/app/docker/api-entrypoint.sh"]
CMD ["uvicorn", "api:app", "--app-dir", "src", "--host", "0.0.0.0", "--port", "8000"]
