# AGENTS.md — hexalate repo guide for AI agents

This file documents the repo layout, key decisions, and operational knowledge for AI agents working on this codebase.

---

## Repo structure (monorepo)

```
hexalate/
├── hexalate/            # Main Python package (PyPI: hexalate)
│   └── hexalate.py      # HexGrid, Hexagon, Orientation, plotting, export, CLI
├── examples/            # Runnable recipe scripts
├── docs/                # GitHub Pages site (james-see.github.io/hexalate)
│   ├── index.html       # Landing page — OG tags, MCP connection instructions
│   ├── playground.html  # Pyodide in-browser REPL
│   ├── llms.txt         # Concise GEO description for LLMs
│   └── llms-full.txt    # Full API reference for LLMs
├── mcp/                 # MCP server sub-package (PyPI: hexalate-mcp)
│   ├── hexalate_mcp/
│   │   ├── server.py    # MCPServer definition + all tools
│   │   ├── __init__.py
│   │   └── __main__.py
│   ├── pyproject.toml   # hexalate-mcp package metadata
│   ├── fly.toml         # Fly.io deployment config (app: hexalate)
│   ├── Dockerfile       # Remote-only build for Fly (via Depot)
│   ├── entrypoint.py    # uvicorn entry for HTTP transport
│   └── Procfile         # web: python entrypoint.py
└── setup.py             # hexalate package metadata
```

---

## Packages & versions

| Package | PyPI | Current version |
|---------|------|-----------------|
| `hexalate` | https://pypi.org/project/hexalate/ | 0.3.0 |
| `hexalate-mcp` | https://pypi.org/project/hexalate-mcp/ | 0.1.1 |

### Publishing a new release

```bash
# hexalate (main package)
# 1. Bump version in setup.py
# 2. Build and publish:
uv build
uv publish --token "$(python3 -c "import configparser,os; c=configparser.ConfigParser(); c.read(os.path.expanduser('~/.pypirc')); print(c['pypi']['password'])")"
git tag v<version> && git push --tags

# hexalate-mcp (MCP server)
cd mcp/
# 1. Bump version in pyproject.toml
# 2. Build and publish:
uv build
rm -f dist/*<old-version>*   # remove any stale artifacts from prior versions
uv publish --token "$(python3 -c "import configparser,os; c=configparser.ConfigParser(); c.read(os.path.expanduser('~/.pypirc')); print(c['pypi']['password'])")"
```

---

## MCP server

### Architecture

The MCP server (`mcp/`) uses **MCP 2.x** (`mcp[cli]>=1.0.0`, resolves to 2.x) with the **streamable HTTP transport** (`POST /mcp`).

Two entry points:
- **stdio** — used by `uvx hexalate-mcp` and local MCP clients. Runs `asyncio.run(mcp.run_stdio_async())`.
- **HTTP** — used by the Fly.io deployment. Runs uvicorn serving `mcp.streamable_http_app()`.

### Critical: DNS rebinding protection (MCP 2.x)

MCP 2.x ships `TransportSecuritySettings` with `enable_dns_rebinding_protection=True` by default. This validates every request's `Host` header against an `allowed_hosts` list. **If `allowed_hosts` is empty, every external request returns `421 Invalid Host header`.**

Always pass an explicit allowlist when deploying:

```python
from mcp.server.transport_security import TransportSecuritySettings

security = TransportSecuritySettings(
    enable_dns_rebinding_protection=True,
    allowed_hosts=[
        "hexalate.fly.dev",
        "localhost",
        "localhost:8080",
        "127.0.0.1",
        "127.0.0.1:8080",
    ],
)
mcp.streamable_http_app(transport_security=security, host="0.0.0.0")
```

Source: `mcp/server/transport_security.py` → `TransportSecurityMiddleware._validate_host`.

### Connecting to the MCP server

**Remote (no install):**
```json
{
  "mcpServers": {
    "hexalate": { "url": "https://hexalate.fly.dev/mcp" }
  }
}
```

**Local via uvx (no install):**
```json
{
  "mcpServers": {
    "hexalate": { "command": "uvx", "args": ["hexalate-mcp"] }
  }
}
```

---

## Fly.io deployment

- **App name:** `hexalate`
- **URL:** https://hexalate.fly.dev
- **MCP endpoint:** `POST https://hexalate.fly.dev/mcp`
- **Region:** `iad` (Washington DC)
- **Machines:** 2 × `shared-cpu-1x` / 512 MB (auto-stop when idle)
- **Build:** Depot remote builder via `--remote-only` (no local Docker needed)

### Deploy command (from repo root)

```bash
export FLY_API_TOKEN="..."   # stored in ~/.cursor or your secrets manager
cd mcp && flyctl deploy --app hexalate --remote-only
```

### Known Fly.io gotchas

1. **Shared IPv4 + 421**: The `*.fly.dev` TLS cert is provisioned automatically, but the proxy only routes to your app once the shared IPv4 is properly registered. If you release and re-allocate the IPv4 (`fly ips allocate-v4 --shared`), DNS may take 1–2 minutes to propagate.

2. **No local Docker needed**: `--remote-only` sends source to Fly's Depot builder. OrbStack / Docker Desktop not required.

3. **Dedicated IPv4 requires billing**: Trial org accounts can only use shared IPv4. `flyctl ips allocate-v4` (without `--shared`) will fail with a billing error.

4. **SSE transport won't work behind Fly's HTTP/2 proxy**: Use the streamable HTTP transport (`mcp.streamable_http_app()`) instead of `mcp.sse_app()`. Fly's edge uses HTTP/2 and SSE over HTTP/2 causes proxy-level failures.

5. **Nixpacks**: Fly supports Nixpacks (`builder = "nixpacks"` in fly.toml) but this requires additional remote-builder auth not available on trial orgs. The Dockerfile approach with `--remote-only` works on all tiers.

---

## GitHub Pages

- **URL:** https://james-see.github.io/hexalate/
- **Source:** `docs/` directory, `main` branch
- **Key files:**
  - `docs/index.html` — landing page with install, API reference, MCP connection snippets
  - `docs/playground.html` — Pyodide REPL (runs hexalate in-browser via WebAssembly)
  - `docs/llms.txt` / `docs/llms-full.txt` — GEO (Generative Engine Optimization) files for LLMs
  - `docs/hero.png` — procedurally generated Civ-style world map (committed asset)
  - `docs/.nojekyll` — disables Jekyll processing

---

## Development notes

- **Python version:** 3.10+ required
- **No ORM** — direct API, no database
- **Linting:** `black` (always run before commits)
- **Local example run:** `pip install -e . && python examples/distance_rings.py`
- **Test MCP endpoint locally:** `uvx hexalate-mcp` (starts stdio server)
- **Test HTTP endpoint locally:** `cd mcp && python entrypoint.py` then `curl -X POST http://localhost:8080/mcp ...`
