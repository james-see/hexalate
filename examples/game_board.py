"""
Game Board (Catan-style)
========================
Assign terrain types to hexagons based on distance zones from the
center and random variation — produces a Settlers of Catan-style
island board. Demonstrates custom per-hex coloring via matplotlib
patches directly.
"""

import math
import random
import matplotlib.pyplot as plt
import matplotlib.patches as patches

import hexalate as hx

random.seed(42)

TERRAIN = {
    "ocean":    "#4a90d9",
    "desert":   "#e8d5a3",
    "plains":   "#c8e66c",
    "forest":   "#2d7a3a",
    "mountain": "#a0a0a0",
    "pasture":  "#8bc34a",
    "hills":    "#c0724a",
}

grid = hx.HexGrid(width=9, height=9, hex_size=0.7, orientation="flat")

cx = sum(h.x for h in grid) / len(grid)
cy = sum(h.y for h in grid) / len(grid)
origin = min(grid, key=lambda h: (h.x - cx) ** 2 + (h.y - cy) ** 2)

land_terrains = ["plains", "forest", "mountain", "pasture", "hills", "desert"]

def terrain_for(h):
    d = origin.distance_to(h)
    if d >= 6:
        return "ocean"
    if d == 0:
        return "desert"
    return random.choice(land_terrains)

fig, ax = plt.subplots(figsize=(10, 10))

for h in grid:
    t = terrain_for(h)
    color = TERRAIN[t]
    ax.add_patch(patches.Polygon(h.coords, edgecolor="white", linewidth=1.5, facecolor=color))

# Legend
from matplotlib.patches import Patch
legend_elements = [Patch(facecolor=c, edgecolor="white", label=t.title()) for t, c in TERRAIN.items()]
ax.legend(handles=legend_elements, loc="lower right", fontsize=9, framealpha=0.85)

xs = [h.x for h in grid]
ys = [h.y for h in grid]
pad = grid.hex_size
ax.set_xlim(min(xs) - pad, max(xs) + pad)
ax.set_ylim(min(ys) - pad, max(ys) + pad)
ax.set_aspect("equal")
ax.axis("off")
ax.set_title("Hex Game Board", fontsize=14, pad=12)
plt.tight_layout()
plt.savefig("game_board.png", dpi=150, bbox_inches="tight", transparent=False)
plt.close()
print(f"Saved game_board.png  ({len(grid)} hexes)")
