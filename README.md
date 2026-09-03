# Hexalate

A Python library for generating hexagonal tessellations with support for axial coordinates, colormap plotting, GeoJSON export, and more.

## Installation

```bash
pip install hexalate
```

## Quick Start

```python
import hexalate as hx

grid = hx.HexGrid(width=10, height=8, hex_size=0.5)
grid.plot()
```

## HexGrid

The main class. Creates a grid that fills a rectangular area.

```python
grid = hx.HexGrid(
    width=10,
    height=8,
    hex_size=0.5,
    orientation="pointy",   # "pointy" (default) or "flat" top
)
```

### Orientation

```python
pointy = hx.HexGrid(10, 8, 0.5, orientation="pointy")  # ⬡ pointy top (default)
flat   = hx.HexGrid(10, 8, 0.5, orientation="flat")    # ⬡ flat top
```

### Iterating and accessing hexagons

```python
for h in grid:
    print(h.x, h.y, h.q, h.r)   # Cartesian center + axial coords

# Access by axial coordinates
h = grid.get(q=0, r=0)

# Get all 6 existing neighbors
neighbors = grid.neighbors(q=0, r=0)
```

### Hexagon properties

Each `Hexagon` dataclass exposes:

| Attribute | Type | Description |
|-----------|------|-------------|
| `x`, `y` | float | Cartesian center |
| `q`, `r` | int | Axial coordinates |
| `s` | int | Third cube coordinate (`-q - r`) |
| `coords` | list | 7 `(x, y)` vertex tuples |

```python
h = grid.get(2, 3)
print(h.s)                       # cube coordinate
print(h.distance_to(grid.get(0, 0)))  # hex distance
print(h.neighbor_coords())       # list of (q, r) neighbor positions
```

### Plotting

```python
# Basic
grid.plot()

# With a colormap driven by per-hex values
import random
values = [random.random() for _ in grid]
grid.plot(values=values, colormap="plasma")

# Save to file instead of showing
grid.plot(output="grid.png", dpi=200)
grid.plot(values=values, colormap="viridis", output="heatmap.svg")

# Convenience shortcut
grid.save_to_file("grid.png", dpi=150)
```

### Export

```python
# Pandas DataFrame (requires pandas)
df = grid.to_dataframe()
# columns: x, y, q, r

# GeoJSON
geojson = grid.to_geojson()   # dict
grid.save_geojson("grid.geojson")

# Backward-compatible list of dicts
data = grid.to_list()
# keys: x, y, q, r, coords
```

## Module-level functions (v0.1 / v0.2 compatible)

The original API still works:

```python
tessellation = hx.create_hexagonal_tessellation(width=10, height=5, hex_size=0.5)
hx.plot_hexagonal_tessellation(tessellation)

# With colormap
import random
values = [random.random() for _ in tessellation]
hx.plot_hexagonal_tessellation(tessellation, colormap="coolwarm", values=values)

# Save to file
hx.plot_hexagonal_tessellation(tessellation, output="grid.png")
```

## Single hexagon

```python
vertices = hx.hexagon(x_center=0.0, y_center=0.0, size=1.0)              # pointy
vertices = hx.hexagon(x_center=0.0, y_center=0.0, size=1.0, orientation="flat")
```

Returns a list of 7 `(x, y)` tuples (closed polygon).

## Command Line

```bash
# Display
hexalate --width 10 --height 8 --size 0.5

# Flat-top orientation
hexalate --width 10 --height 8 --size 0.5 --orientation flat

# Random colormap coloring
hexalate --width 10 --height 8 --size 0.5 --colormap plasma

# Save to file
hexalate --width 10 --height 8 --size 0.5 --output grid.png
hexalate --width 10 --height 8 --size 0.5 --colormap viridis --output heatmap.svg
```

## License

MIT License.
