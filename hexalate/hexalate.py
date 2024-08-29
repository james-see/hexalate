import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import argparse

def hexagon(x_center, y_center, size):
    """
    Generates the coordinates of a hexagon.

    Args:
        x_center (float): The x-coordinate of the hexagon's center.
        y_center (float): The y-coordinate of the hexagon's center.
        size (float): The radius of the hexagon.

    Returns:
        list: A list of tuples representing the hexagon's vertices.
    """
    angle = np.linspace(0, 2 * np.pi, 7)
    x = x_center + size * np.cos(angle)
    y = y_center + size * np.sin(angle)
    return list(zip(x, y))

def create_hexagonal_tessellation(width, height, hex_size):
    """
    Generates a hexagonal tessellation that fills a specified area.

    Args:
        width (float): The width of the area to be filled.
        height (float): The height of the area to be filled.
        hex_size (float): The radius of the hexagons in the tessellation.

    Returns:
        list: A list of dictionaries, each representing a hexagon with its coordinates.
    """
    # Calculate the horizontal and vertical spacing between hexagon centers
    horiz_spacing = hex_size * 3/2
    vert_spacing = hex_size * np.sqrt(3)
    
    # Calculate the number of rows and columns needed to fill the area
    num_cols = int(width / horiz_spacing) + 2
    num_rows = int(height / vert_spacing) + 2
    
    tessellation = []
    for row in range(num_rows):
        for col in range(num_cols):
            x = col * horiz_spacing
            y = row * vert_spacing
            
            # Offset every other column
            if col % 2 == 1:
                y += vert_spacing / 2
            
            hex_coords = hexagon(x, y, hex_size)
            tessellation.append({'x': x, 'y': y, 'coords': hex_coords})

    return tessellation

def plot_hexagonal_tessellation(tessellation):
    """
    Plots a hexagonal tessellation.

    Args:
        tessellation (list): A list of dictionaries, each representing a hexagon with its coordinates.
    """
    fig, ax = plt.subplots(figsize=(10, 8))
    
    for hexagon in tessellation:
        ax.add_patch(patches.Polygon(hexagon['coords'], edgecolor='black', facecolor='lightblue'))

    ax.set_xlim(0, max([hexagon['x'] for hexagon in tessellation]) + 1)
    ax.set_ylim(0, max([hexagon['y'] for hexagon in tessellation]) + 1)
    ax.set_aspect('equal')
    plt.axis('off')
    plt.tight_layout()
    plt.show()


def main():
    parser = argparse.ArgumentParser(description='Generate a hexagonal tessellation.')
    parser.add_argument('--width', type=float, required=True, help='The width of the tessellation.')
    parser.add_argument('--height', type=float, required=True, help='The height of the tessellation.')
    parser.add_argument('--size', type=float, required=True, help='The radius of the hexagons.')
    args = parser.parse_args()

    tessellation = create_hexagonal_tessellation(args.width, args.height, args.size)
    plot_hexagonal_tessellation(tessellation)


if __name__ == "__main__":
    main()
