FROM python:3.12-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir "hexalate>=0.3.0" "mcp[cli]" uvicorn starlette h11
ENV PORT=8080
CMD ["python", "entrypoint.py"]
