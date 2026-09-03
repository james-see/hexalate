"""
Wave Heatmap
============
Map a mathematical function (sin × cos) over the grid to produce a
smooth, undulating heatmap. Swap in any function of (x, y) — elevation
data, sensor readings, probability density, etc.
"""

import math
import hexalate as hx

grid = hx.HexGrid(width=12, height=10, hex_size=0.5)

# sin(x) * cos(y) — one full wave cycle across the grid
values = [math.sin(h.x * 0.8) * math.cos(h.y * 0.8) for h in grid]

grid.plot(
    values=values,
    colormap="RdYlBu",
    edge_color="none",
    figsize=(12, 9),
    output="wave_heatmap.png",
)
print(f"Saved wave_heatmap.png  ({len(grid)} hexes)")
