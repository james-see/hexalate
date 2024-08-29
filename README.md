# Hexalate
A Python library for generating hexagonal tessellations.

## Features

- Generate coordinates for individual hexagons
- Create a tessellation that fills a specified area with hexagons of a specific size
- Supports customization of hexagon shape and size

## Installation

To use this library, simply install it using pip:

```bash
pip install cayleygraph
```

## Usage

### Basic Usage

Import the `hexalate` module:

```python
import cayleygraph as cg
```

Create a tessellation with the desired width, height, and hexagon size:

```python
width = 10
height = 5
size = 0.3
tessellation = cg.create_hexagonal_tessellation(width, height, size)
```

Visualize the tessellation using your favorite plotting library (e.g., Matplotlib):

```python
import matplotlib.pyplot as plt

plt.figure(figsize=(width, height))
for hexagon in tessellation:
    x, y = hexagon['x'], hexagon['y']
    plt.plot([x, x+size*np.sqrt(3)], [y, y+size/2], 'k-')
    plt.plot([x, x+size*np.sqrt(3)/2], [y-size/4, y+size/4], 'k-')
    plt.plot([x, x-size*np.sqrt(3)/2], [y-size/4, y+size/4], 'k-')
plt.show()
```

### Advanced Usage

Customize the hexagon shape and size:

```python

hexagon = cg.hexagon(center=(1, 2), size=0.5)
```

Generate a tessellation with a specific density:

```python
density = 0.8
tessellation = cg.create_hexagonal_tessellation(width, height, size, density=density)
```

### Acknowledgments

This library is based on the work of Cayley, a mathematician who developed the concept of Cayley graphs. Special thanks to MATLAB for inspiring the naming conventions and syntax.

### License

This library is released under the MIT License. For more information, see the LICENSE file.
