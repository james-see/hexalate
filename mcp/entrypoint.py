"""Fly.io entrypoint — serves hexalate MCP over streamable HTTP (POST /mcp)."""
import os
import uvicorn
from hexalate_mcp.server import create_http_app

app = create_http_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
