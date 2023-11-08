FROM chromadb/chroma:latest

CMD ["uvicorn", "chromadb.app:app", "--reload", "--workers","1", "--host", "0.0.0.0", "--port", "8000", "--log-config", "/log_config.yml"]
