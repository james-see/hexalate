"""
hexalate MCP server — exposes hexalate tools to any MCP-compatible client
(Cursor, Claude Desktop, etc.).

Run locally via uvx:
    uvx hexalate-mcp

Add to Cursor / Claude Desktop MCP config:
    {
      "mcpServers": {
        "hexalate": { "command": "uvx", "args": ["hexalate-mcp"] }
      }
    }

Or connect to the hosted remote server:
    {
      "mcpServers": {
        "hexalate": { "url": "https://hexalate-mcp.james-see.run/sse" }
      }
    }
"""

from __future__ import annotations

import asyncio
import json
import math
import os
import tempfile
from typing import Any

import hexalate as hx
from mcp.server.mcpserver import MCPServer

mcp = MCPServer(
    name="hexalate",
    title="Hexalate",
    description="Hexagonal tessellation tools — create grids, query axial coordinates, export GeoJSON, plot heatmaps.",
    version="0.1.0",
    website_url="https://james-see.github.io/hexalate/",
)

# ---------------------------------------------------------------------------
# In-memory grid store — grids are referenced by name across tool calls
# ---------------------------------------------------------------------------
_grids: dict[str, hx.HexGrid] = {}


def _require(name: str) -> hx.HexGrid:
    if name not in _grids:
        keys = list(_grids.keys())
        raise ValueError(
            f"No grid named '{name}'. "
            f"Available: {keys if keys else ['(none — call create_grid first)']}"
        )
    return _grids[name]


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------

@mcp.tool()
def create_grid(
    width: float,
    height: float,
    hex_size: float,
    orientation: str = "pointy",
    name: str = "default",
) -> str:
    """
    Create a hexagonal grid and store it under a name for use by other tools.

    Args:
        width: Width of the area to fill.
        height: Height of the area to fill.
        hex_size: Circumradius of each hexagon.
        orientation: "pointy" (default) or "flat" top.
        name: Reference name for this grid (default: "default").
    """
    if orientation not in ("pointy", "flat"):
        raise ValueError("orientation must be 'pointy' or 'flat'")
    grid = hx.HexGrid(width=width, height=height, hex_size=hex_size, orientation=orientation)
    _grids[name] = grid
    xs = [h.x for h in grid]
    ys = [h.y for h in grid]
    return (
        f"Created grid '{name}': {len(grid)} hexagons, orientation={orientation}, "
        f"hex_size={hex_size}, "
        f"bbox x=[{min(xs):.2f}, {max(xs):.2f}] y=[{min(ys):.2f}, {max(ys):.2f}]"
    )


@mcp.tool()
def list_grids() -> str:
    """List all grids currently in memory."""
    if not _grids:
        return "No grids in memory. Call create_grid first."
    lines = []
    for name, grid in _grids.items():
        lines.append(f"  '{name}': {len(grid)} hexes, orientation={grid.orientation}, hex_size={grid.hex_size}")
    return "Grids in memory:\n" + "\n".join(lines)


@mcp.tool()
def get_hex(q: int, r: int, grid_name: str = "default") -> str:
    """
    Get details about the hexagon at axial coordinates (q, r).

    Args:
        q: Axial column coordinate.
        r: Axial row coordinate.
        grid_name: Name of the grid (default: "default").
    """
    grid = _require(grid_name)
    h = grid.get(q, r)
    if h is None:
        return f"No hexagon at ({q}, {r}) in grid '{grid_name}'."
    ns = grid.neighbors(q, r)
    return (
        f"Hexagon at axial ({q}, {r}):\n"
        f"  Cartesian center: ({h.x:.4f}, {h.y:.4f})\n"
        f"  Cube coords: q={h.q}, r={h.r}, s={h.s}\n"
        f"  Neighbors in grid: {len(ns)} "
        f"[{', '.join(f'({n.q},{n.r})' for n in ns)}]"
    )


@mcp.tool()
def neighbors(q: int, r: int, grid_name: str = "default") -> str:
    """
    Return all existing neighbors of the hexagon at axial (q, r).

    Args:
        q: Axial column coordinate.
        r: Axial row coordinate.
        grid_name: Name of the grid (default: "default").
    """
    grid = _require(grid_name)
    h = grid.get(q, r)
    if h is None:
        return f"No hexagon at ({q}, {r}) in grid '{grid_name}'."
    ns = grid.neighbors(q, r)
    if not ns:
        return f"Hexagon at ({q}, {r}) has no neighbors within the grid bounds."
    lines = [f"Neighbors of ({q}, {r}) — {len(ns)} found:"]
    for n in ns:
        lines.append(f"  ({n.q}, {n.r})  center=({n.x:.3f}, {n.y:.3f})")
    return "\n".join(lines)


@mcp.tool()
def distance(q1: int, r1: int, q2: int, r2: int, grid_name: str = "default") -> str:
    """
    Return the hex (cube-coordinate) distance between two hexagons.

    Args:
        q1: Axial column of first hex.
        r1: Axial row of first hex.
        q2: Axial column of second hex.
        r2: Axial row of second hex.
        grid_name: Name of the grid (default: "default").
    """
    grid = _require(grid_name)
    a = grid.get(q1, r1)
    b = grid.get(q2, r2)
    if a is None:
        return f"No hexagon at ({q1}, {r1})."
    if b is None:
        return f"No hexagon at ({q2}, {r2})."
    return f"Hex distance from ({q1},{r1}) to ({q2},{r2}): {a.distance_to(b)} steps"


@mcp.tool()
def ring(q: int, r: int, radius: int, grid_name: str = "default") -> str:
    """
    Return all hexagons exactly `radius` steps from the hex at (q, r).

    Args:
        q: Center hex axial column.
        r: Center hex axial row.
        radius: Ring distance (0 returns just the center hex).
        grid_name: Name of the grid (default: "default").
    """
    grid = _require(grid_name)
    center = grid.get(q, r)
    if center is None:
        return f"No hexagon at ({q}, {r})."
    hexes = [h for h in grid if center.distance_to(h) == radius]
    if not hexes:
        return f"No hexagons at distance {radius} from ({q},{r}) within the grid."
    coords = ", ".join(f"({h.q},{h.r})" for h in hexes)
    return f"Ring radius={radius} around ({q},{r}): {len(hexes)} hexes — {coords}"


@mcp.tool()
def grid_stats(grid_name: str = "default") -> str:
    """
    Return statistics for a grid: hex count, bounding box, axial coordinate ranges.

    Args:
        grid_name: Name of the grid (default: "default").
    """
    grid = _require(grid_name)
    xs = [h.x for h in grid]
    ys = [h.y for h in grid]
    qs = [h.q for h in grid]
    rs = [h.r for h in grid]
    return (
        f"Grid '{grid_name}':\n"
        f"  Hexagons: {len(grid)}\n"
        f"  Orientation: {grid.orientation}\n"
        f"  Hex size: {grid.hex_size}\n"
        f"  Cartesian bbox: x=[{min(xs):.3f}, {max(xs):.3f}]  y=[{min(ys):.3f}, {max(ys):.3f}]\n"
        f"  Axial q range: [{min(qs)}, {max(qs)}]\n"
        f"  Axial r range: [{min(rs)}, {max(rs)}]"
    )


@mcp.tool()
def to_geojson(output_path: str, grid_name: str = "default") -> str:
    """
    Export a grid to a GeoJSON file.

    Args:
        output_path: File path to write (e.g. "/tmp/grid.geojson").
        grid_name: Name of the grid (default: "default").
    """
    grid = _require(grid_name)
    grid.save_geojson(output_path)
    return f"Saved GeoJSON to {output_path} ({len(grid)} features)"


@mcp.tool()
def plot_grid(
    output_path: str,
    grid_name: str = "default",
    colormap: str = "viridis",
    color_by: str = "none",
    dpi: int = 150,
) -> str:
    """
    Plot a grid and save it to a file.

    Args:
        output_path: Path to save the image (.png, .svg, .pdf).
        grid_name: Name of the grid (default: "default").
        colormap: Matplotlib colormap (e.g. viridis, plasma, coolwarm, RdYlBu).
        color_by: What to color hexes by — "none" (uniform), "distance" (from center),
                  "q" (axial q coord), "r" (axial r coord), "wave" (sin*cos pattern).
        dpi: Resolution when saving (default 150).
    """
    grid = _require(grid_name)

    values = None
    if color_by != "none":
        if color_by == "distance":
            xs = [h.x for h in grid]
            ys = [h.y for h in grid]
            cx = sum(xs) / len(xs)
            cy = sum(ys) / len(ys)
            origin = min(grid, key=lambda h: (h.x - cx) ** 2 + (h.y - cy) ** 2)
            values = [origin.distance_to(h) for h in grid]
        elif color_by == "q":
            values = [float(h.q) for h in grid]
        elif color_by == "r":
            values = [float(h.r) for h in grid]
        elif color_by == "wave":
            values = [math.sin(h.x * 0.8) * math.cos(h.y * 0.8) for h in grid]
        else:
            raise ValueError(f"color_by must be one of: none, distance, q, r, wave")

    grid.plot(values=values, colormap=colormap, output=output_path, dpi=dpi)
    size_kb = os.path.getsize(output_path) // 1024
    return f"Saved plot to {output_path} ({size_kb} KB)"


# ---------------------------------------------------------------------------
# Entry points
# ---------------------------------------------------------------------------

def create_http_app():
    """Return the streamable HTTP ASGI app (MCP 2.x, POST /mcp, Fly.io compatible)."""
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
    return mcp.streamable_http_app(transport_security=security, host="0.0.0.0")


def create_sse_app():
    """Alias kept for compatibility — returns streamable HTTP app."""
    return create_http_app()


def main() -> None:
    """stdio entry point — used by uvx / local MCP."""
    asyncio.run(mcp.run_stdio_async())


if __name__ == "__main__":
    main()
