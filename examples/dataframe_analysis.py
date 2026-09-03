"""
DataFrame Analysis
==================
Export the grid to a pandas DataFrame, attach custom data,
filter/sort/group with normal pandas operations, then re-plot
only the hexes you care about.

Requires: pip install pandas
"""

import math
import hexalate as hx

grid = hx.HexGrid(width=14, height=10, hex_size=0.5)

# Get base dataframe
df = grid.to_dataframe()

# Attach a custom metric — distance from Cartesian origin
df["dist_from_origin"] = (df["x"] ** 2 + df["y"] ** 2) ** 0.5

# Attach a "zone" label based on cube ring distance
hexes = list(grid)
cx = df["x"].mean()
cy = df["y"].mean()
origin_hex = min(hexes, key=lambda h: (h.x - cx) ** 2 + (h.y - cy) ** 2)
df["ring"] = [origin_hex.distance_to(h) for h in hexes]

print(df.head(10).to_string())
print(f"\nTotal hexes : {len(df)}")
print(f"Ring 0 (center) : {len(df[df['ring'] == 0])}")
print(f"Ring 1          : {len(df[df['ring'] == 1])}")
print(f"Ring 2          : {len(df[df['ring'] == 2])}")
print(f"\nMean dist from origin: {df['dist_from_origin'].mean():.2f}")
print(f"Hexes in top 25% furthest: {len(df[df['dist_from_origin'] > df['dist_from_origin'].quantile(0.75)])}")

# Plot only the inner 3 rings as a sub-grid
inner_qr = set(zip(df[df["ring"] <= 3]["q"], df[df["ring"] <= 3]["r"]))
inner_hexes = [h for h in hexes if (h.q, h.r) in inner_qr]

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.colors as mcolors

inner_rings = [origin_hex.distance_to(h) for h in inner_hexes]
norm = mcolors.Normalize(vmin=0, vmax=max(inner_rings))
cmap = plt.get_cmap("YlOrRd")

fig, ax = plt.subplots(figsize=(7, 7))
for h, ring in zip(inner_hexes, inner_rings):
    ax.add_patch(patches.Polygon(h.coords, edgecolor="white", linewidth=1.2, facecolor=cmap(norm(ring))))

sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
sm.set_array([])
plt.colorbar(sm, ax=ax, fraction=0.03, pad=0.02, label="Ring distance")

xs = [h.x for h in inner_hexes]
ys = [h.y for h in inner_hexes]
pad = grid.hex_size
ax.set_xlim(min(xs) - pad, max(xs) + pad)
ax.set_ylim(min(ys) - pad, max(ys) + pad)
ax.set_aspect("equal")
ax.axis("off")
ax.set_title("Inner 3 rings (filtered via DataFrame)", fontsize=12)
plt.tight_layout()
plt.savefig("dataframe_analysis.png", dpi=150, bbox_inches="tight")
plt.close()
print("\nSaved dataframe_analysis.png")
