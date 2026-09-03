"""
GeoJSON Export
==============
Export a hex grid as GeoJSON, then load it back and filter to only
hexes within a given distance of the center. Shows how to combine
hexalate with standard geo tooling (GeoPandas, Folium, QGIS, etc.).
"""

import json
import hexalate as hx

grid = hx.HexGrid(width=15, height=12, hex_size=0.6)

# Save full grid
grid.save_geojson("full_grid.geojson")
print(f"Saved full_grid.geojson  ({len(grid)} hexes)")

# Build a filtered GeoJSON — only hexes within 4 steps of center
cx = sum(h.x for h in grid) / len(grid)
cy = sum(h.y for h in grid) / len(grid)
origin = min(grid, key=lambda h: (h.x - cx) ** 2 + (h.y - cy) ** 2)

features = []
for h in grid:
    d = origin.distance_to(h)
    if d <= 4:
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": [[(x, y) for x, y in h.coords]],
            },
            "properties": {"q": h.q, "r": h.r, "distance": d},
        })

filtered = {"type": "FeatureCollection", "features": features}
with open("center_zone.geojson", "w") as f:
    json.dump(filtered, f, indent=2)

print(f"Saved center_zone.geojson ({len(features)} hexes within distance 4)")

# Tip: open either file in QGIS, kepler.gl, or geojson.io for instant visualisation
