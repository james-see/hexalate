# hexalate-mcp

MCP server for [hexalate](https://james-see.github.io/hexalate/) — hexagonal tessellation tools for AI assistants (Cursor, Claude Desktop, etc.).

## Install & connect

### Local (stdio) — recommended

Add to your Cursor or Claude Desktop MCP config:

```json
{
  "mcpServers": {
    "hexalate": {
      "command": "uvx",
      "args": ["hexalate-mcp"]
    }
  }
}
```

Or run directly:
```bash
pip install hexalate-mcp
hexalate-mcp
```

### Remote (HTTP+SSE)

A hosted instance runs at `https://hexalate-mcp.james-see.run`. Add to your config:

```json
{
  "mcpServers": {
    "hexalate": {
      "url": "https://hexalate-mcp.james-see.run/sse"
    }
  }
}
```

## Tools

| Tool | Description |
|------|-------------|
| `create_grid` | Create a hex grid (width, height, hex_size, orientation) |
| `list_grids` | List all grids currently in memory |
| `get_hex` | Get details about the hex at axial (q, r) |
| `neighbors` | Get all existing neighbors of a hex |
| `distance` | Cube-coordinate distance between two hexes |
| `ring` | All hexes exactly N steps from a center hex |
| `grid_stats` | Bounding box, hex count, coord ranges |
| `to_geojson` | Export grid to GeoJSON (inline or file) |
| `plot_grid` | Plot the grid — color by distance/q/r/wave, save to file |

## Example prompts

- *"Create a 10×8 flat-top hex grid with size 0.6 and plot it colored by distance from center"*
- *"What are the neighbors of hex (2, 3)?"*
- *"Give me the distance between (0,0) and (5,3)"*
- *"Export my grid as GeoJSON and save it to ~/grid.geojson"*
- *"Show me all hexes in ring 3 around the center"*

## License

MIT
