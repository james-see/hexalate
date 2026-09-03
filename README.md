# Hexalate
A Python library for generating hexagonal tessellations.

## Features

- Generate coordinates for individual hexagons
- Create a tessellation that fills a specified area with hexagons of a specific size
- Supports customization of hexagon shape and size

## Installation

To use this library, simply install it using pip:

```bash
pip install hexalate
```

## Usage

### Basic Usage

Import the `hexalate` module:

```python
import hexalate as hx
```

Create and visualize a tessellation with the desired width, height, and hexagon size:

```python
tessellation = hx.create_hexagonal_tessellation(width=10, height=5, hex_size=0.5)
hx.plot_hexagonal_tessellation(tessellation)
```

### Generate Hexagon Coordinates

Get the vertices of a single hexagon centered at `(x, y)` with a given radius:

```python
vertices = hx.hexagon(x_center=1.0, y_center=2.0, size=0.5)
```

Returns a list of `(x, y)` tuples for the 7 vertices (closed polygon).

### Advanced Usage

Access the raw tessellation data to integrate with your own plotting library:

```python
import matplotlib.pyplot as plt
import matplotlib.patches as patches

tessellation = hx.create_hexagonal_tessellation(width=10, height=8, hex_size=0.6)

fig, ax = plt.subplots(figsize=(10, 8))
for hex_data in tessellation:
    ax.add_patch(patches.Polygon(hex_data['coords'], edgecolor='black', facecolor='lightblue'))
ax.autoscale_view()
ax.set_aspect('equal')
plt.axis('off')
plt.show()
```

Each element in the tessellation list is a dict with keys:
- `x` — center x coordinate
- `y` — center y coordinate
- `coords` — list of `(x, y)` vertex tuples

### Command Line

```bash
hexalate --width 10 --height 8 --size 0.5
```

### License

This library is released under the MIT License. For more information, see the LICENSE file.
