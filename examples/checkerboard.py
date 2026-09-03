"""
Checkerboard (3-color)
======================
Hex grids can be 3-colored so no two adjacent hexes share a color.
Uses (q mod 3) derived from axial coordinates — no adjacency checks needed.
Useful for game mechanics, visual patterns, or zone highlighting.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches

import hexalate as hx

COLORS = ["#e74c3c", "#3498db", "#2ecc71"]   # red / blue / green

grid = hx.HexGrid(width=12, height=10, hex_size=0.55)

fig, ax = plt.subplots(figsize=(12, 9))

for h in grid:
    color = COLORS[((h.q % 3) + 3) % 3]   # keep positive for negative q values
    ax.add_patch(patches.Polygon(h.coords, edgecolor="white", linewidth=0.8, facecolor=color))

xs = [h.x for h in grid]
ys = [h.y for h in grid]
pad = grid.hex_size
ax.set_xlim(min(xs) - pad, max(xs) + pad)
ax.set_ylim(min(ys) - pad, max(ys) + pad)
ax.set_aspect("equal")
ax.axis("off")
ax.set_title("3-Color Hex Checkerboard", fontsize=13, pad=10)
plt.tight_layout()
plt.savefig("checkerboard.png", dpi=150, bbox_inches="tight")
plt.close()
print(f"Saved checkerboard.png  ({len(grid)} hexes)")
