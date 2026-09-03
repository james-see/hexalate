"""
Distance Rings
==============
Color every hexagon by its cube-coordinate distance from the center hex.
Produces concentric "rings" radiating outward — great for range indicators
in board games or influence maps.
"""

import hexalate as hx

grid = hx.HexGrid(width=10, height=10, hex_size=0.6)

# Find the hex closest to the Cartesian center of the grid
cx = sum(h.x for h in grid) / len(grid)
cy = sum(h.y for h in grid) / len(grid)
origin = min(grid, key=lambda h: (h.x - cx) ** 2 + (h.y - cy) ** 2)

values = [origin.distance_to(h) for h in grid]

grid.plot(
    values=values,
    colormap="coolwarm",
    edge_color="#333333",
    figsize=(8, 8),
    output="distance_rings.png",
)
print(f"Saved distance_rings.png  ({len(grid)} hexes, max distance {max(values)})")
