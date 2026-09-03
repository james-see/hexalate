from __future__ import annotations

import json
import math
from dataclasses import dataclass
from typing import Literal, Optional

import matplotlib.colors as mcolors
import matplotlib.patches as patches
import matplotlib.pyplot as plt
import numpy as np
import argparse


Orientation = Literal["pointy", "flat"]


# ---------------------------------------------------------------------------
# Hexagon dataclass
# ---------------------------------------------------------------------------

@dataclass
class Hexagon:
    """A single hexagon in a HexGrid."""

    x: float          # Cartesian center x
    y: float          # Cartesian center y
    q: int            # axial column coordinate
    r: int            # axial row coordinate
    coords: list      # list of 7 (x, y) vertex tuples (closed polygon)

    @property
    def s(self) -> int:
        """Third cube coordinate. Always -q - r."""
        return -self.q - self.r

    def neighbor_coords(self) -> list[tuple[int, int]]:
        """Return axial (q, r) pairs for all 6 neighbors."""
        directions = [(1, 0), (1, -1), (0, -1), (-1, 0), (-1, 1), (0, 1)]
        return [(self.q + dq, self.r + dr) for dq, dr in directions]

    def distance_to(self, other: Hexagon) -> int:
        """Cube-coordinate distance between this hex and another."""
        return max(abs(self.q - other.q), abs(self.r - other.r), abs(self.s - other.s))

    def to_dict(self) -> dict:
        return {"x": self.x, "y": self.y, "q": self.q, "r": self.r, "coords": self.coords}


# ---------------------------------------------------------------------------
# Vertex generation
# ---------------------------------------------------------------------------

def _hex_vertices(
    x_center: float,
    y_center: float,
    size: float,
    orientation: Orientation = "pointy",
) -> list[tuple[float, float]]:
    offset = math.pi / 6 if orientation == "pointy" else 0.0
    angles = [math.pi / 3 * i + offset for i in range(7)]
    return [(x_center + size * math.cos(a), y_center + size * math.sin(a)) for a in angles]


def hexagon(
    x_center: float,
    y_center: float,
    size: float,
    orientation: Orientation = "pointy",
) -> list[tuple[float, float]]:
    """
    Generate the vertices of a single hexagon.

    Args:
        x_center: Center x coordinate.
        y_center: Center y coordinate.
        size: Circumradius of the hexagon.
        orientation: "pointy" (default) or "flat" top.

    Returns:
        List of 7 (x, y) tuples forming a closed polygon.
    """
    return _hex_vertices(x_center, y_center, size, orientation)


# ---------------------------------------------------------------------------
# HexGrid class
# ---------------------------------------------------------------------------

class HexGrid:
    """
    A hexagonal tessellation grid.

    Args:
        width: Width of the area to fill.
        height: Height of the area to fill.
        hex_size: Circumradius of each hexagon.
        orientation: "pointy" (default) or "flat" top.

    Examples:
        >>> grid = HexGrid(10, 8, 0.5)
        >>> grid.plot()

        >>> grid = HexGrid(10, 8, 0.5, orientation="flat")
        >>> df = grid.to_dataframe()

        >>> h = grid.get(0, 0)
        >>> grid.neighbors(0, 0)
    """

    def __init__(
        self,
        width: float,
        height: float,
        hex_size: float,
        orientation: Orientation = "pointy",
    ) -> None:
        self.width = width
        self.height = height
        self.hex_size = hex_size
        self.orientation = orientation
        self._hexagons: list[Hexagon] = []
        self._index: dict[tuple[int, int], Hexagon] = {}
        self._generate()

    # ------------------------------------------------------------------
    # Grid generation
    # ------------------------------------------------------------------

    def _generate(self) -> None:
        size = self.hex_size
        self._hexagons = []
        self._index = {}

        if self.orientation == "pointy":
            horiz_spacing = size * math.sqrt(3)
            vert_spacing = size * 3 / 2
            num_cols = int(self.width / horiz_spacing) + 2
            num_rows = int(self.height / vert_spacing) + 2
            for row in range(num_rows):
                for col in range(num_cols):
                    x = col * horiz_spacing
                    if row % 2 == 1:
                        x += horiz_spacing / 2
                    y = row * vert_spacing
                    # odd-r offset → axial
                    q = col - (row - (row & 1)) // 2
                    r = row
                    coords = _hex_vertices(x, y, size, "pointy")
                    h = Hexagon(x=x, y=y, q=q, r=r, coords=coords)
                    self._hexagons.append(h)
                    self._index[(q, r)] = h
        else:
            # flat-top: odd-q offset
            horiz_spacing = size * 3 / 2
            vert_spacing = size * math.sqrt(3)
            num_cols = int(self.width / horiz_spacing) + 2
            num_rows = int(self.height / vert_spacing) + 2
            for col in range(num_cols):
                for row in range(num_rows):
                    x = col * horiz_spacing
                    y = row * vert_spacing
                    if col % 2 == 1:
                        y += vert_spacing / 2
                    # odd-q offset → axial
                    q = col
                    r = row - (col - (col & 1)) // 2
                    coords = _hex_vertices(x, y, size, "flat")
                    h = Hexagon(x=x, y=y, q=q, r=r, coords=coords)
                    self._hexagons.append(h)
                    self._index[(q, r)] = h

    # ------------------------------------------------------------------
    # Access & navigation
    # ------------------------------------------------------------------

    def __len__(self) -> int:
        return len(self._hexagons)

    def __iter__(self):
        return iter(self._hexagons)

    def get(self, q: int, r: int) -> Optional[Hexagon]:
        """Return the Hexagon at axial (q, r), or None if out of bounds."""
        return self._index.get((q, r))

    def neighbors(self, q: int, r: int) -> list[Hexagon]:
        """Return all existing neighbor Hexagons for the hex at (q, r)."""
        h = self.get(q, r)
        if h is None:
            return []
        return [self._index[n] for n in h.neighbor_coords() if n in self._index]

    # ------------------------------------------------------------------
    # Export
    # ------------------------------------------------------------------

    def to_list(self) -> list[dict]:
        """Return the grid as a list of dicts (backward-compatible format)."""
        return [h.to_dict() for h in self._hexagons]

    def to_dataframe(self):
        """
        Return a pandas DataFrame with columns: x, y, q, r.

        Requires pandas (pip install pandas).
        """
        try:
            import pandas as pd
        except ImportError:
            raise ImportError("pandas is required: pip install pandas")
        return pd.DataFrame(
            [{"x": h.x, "y": h.y, "q": h.q, "r": h.r} for h in self._hexagons]
        )

    def to_geojson(self) -> dict:
        """Return the grid as a GeoJSON FeatureCollection dict."""
        features = [
            {
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[(cx, cy) for cx, cy in h.coords]],
                },
                "properties": {"q": h.q, "r": h.r, "x": h.x, "y": h.y},
            }
            for h in self._hexagons
        ]
        return {"type": "FeatureCollection", "features": features}

    def save_geojson(self, path: str) -> None:
        """Write the grid to a GeoJSON file at ``path``."""
        with open(path, "w") as f:
            json.dump(self.to_geojson(), f, indent=2)

    # ------------------------------------------------------------------
    # Plotting
    # ------------------------------------------------------------------

    def plot(
        self,
        values: Optional[list[float]] = None,
        colormap: str = "viridis",
        edge_color: str = "black",
        face_color: str = "lightblue",
        figsize: tuple[float, float] = (10, 8),
        output: Optional[str] = None,
        dpi: int = 150,
    ) -> None:
        """
        Plot the tessellation.

        Args:
            values: Optional list of floats (one per hexagon) to drive colormap
                    coloring. When provided, ``face_color`` is ignored.
            colormap: Matplotlib colormap name used when ``values`` is given
                      (default "viridis").
            edge_color: Hex border color (default "black").
            face_color: Uniform fill color when no ``values`` are provided.
            figsize: Figure size ``(width, height)`` in inches.
            output: File path to save the plot instead of displaying it.
                    Supports any format matplotlib accepts (.png, .svg, .pdf…).
            dpi: Resolution when saving to a file (default 150).
        """
        fig, ax = plt.subplots(figsize=figsize)

        cmap = norm = sm = None
        if values is not None:
            if len(values) != len(self._hexagons):
                raise ValueError(
                    f"len(values)={len(values)} must equal grid size {len(self._hexagons)}"
                )
            norm = mcolors.Normalize(vmin=min(values), vmax=max(values))
            cmap = plt.get_cmap(colormap)
            sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
            sm.set_array([])

        for i, h in enumerate(self._hexagons):
            color = cmap(norm(values[i])) if cmap is not None else face_color
            ax.add_patch(patches.Polygon(h.coords, edgecolor=edge_color, facecolor=color))

        xs = [h.x for h in self._hexagons]
        ys = [h.y for h in self._hexagons]
        pad = self.hex_size
        ax.set_xlim(min(xs) - pad, max(xs) + pad)
        ax.set_ylim(min(ys) - pad, max(ys) + pad)
        ax.set_aspect("equal")
        plt.axis("off")

        if sm is not None:
            plt.colorbar(sm, ax=ax, fraction=0.03, pad=0.02)

        plt.tight_layout()

        if output:
            plt.savefig(output, dpi=dpi, bbox_inches="tight", transparent=True)
            plt.close(fig)
        else:
            plt.show()

    def save_to_file(self, path: str, dpi: int = 150, **kwargs) -> None:
        """
        Save the tessellation plot to an image file.

        Args:
            path: Output path (.png, .svg, .pdf, etc.).
            dpi: Resolution (default 150).
            **kwargs: Additional keyword arguments passed to ``plot()``.
        """
        self.plot(output=path, dpi=dpi, **kwargs)


# ---------------------------------------------------------------------------
# Backward-compatible module-level functions
# ---------------------------------------------------------------------------

def create_hexagonal_tessellation(
    width: float,
    height: float,
    hex_size: float,
    orientation: Orientation = "pointy",
) -> list[dict]:
    """
    Generate a hexagonal tessellation (backward-compatible).

    Returns:
        List of dicts with keys: x, y, q, r, coords.
    """
    return HexGrid(width, height, hex_size, orientation).to_list()


def plot_hexagonal_tessellation(
    tessellation: list[dict],
    colormap: Optional[str] = None,
    values: Optional[list[float]] = None,
    output: Optional[str] = None,
) -> None:
    """
    Plot a tessellation returned by ``create_hexagonal_tessellation``.

    Args:
        tessellation: List of hex dicts.
        colormap: Matplotlib colormap name (e.g. "plasma"). Required when
                  ``values`` is provided.
        values: Per-hexagon float values driving colormap coloring.
        output: Optional file path to save instead of displaying.
    """
    fig, ax = plt.subplots(figsize=(10, 8))

    cmap = norm = sm = None
    if values is not None and colormap is not None:
        norm = mcolors.Normalize(vmin=min(values), vmax=max(values))
        cmap = plt.get_cmap(colormap)
        sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
        sm.set_array([])

    for i, h in enumerate(tessellation):
        color = cmap(norm(values[i])) if cmap is not None else "lightblue"
        ax.add_patch(patches.Polygon(h["coords"], edgecolor="black", facecolor=color))

    xs = [h["x"] for h in tessellation]
    ys = [h["y"] for h in tessellation]
    ax.set_xlim(min(xs) - 1, max(xs) + 1)
    ax.set_ylim(min(ys) - 1, max(ys) + 1)
    ax.set_aspect("equal")
    plt.axis("off")

    if sm is not None:
        plt.colorbar(sm, ax=ax, fraction=0.03, pad=0.02)

    plt.tight_layout()

    if output:
        plt.savefig(output, dpi=150, bbox_inches="tight", transparent=True)
        plt.close(fig)
    else:
        plt.show()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a hexagonal tessellation.")
    parser.add_argument("--width",       type=float, required=True,  help="Width of the tessellation area.")
    parser.add_argument("--height",      type=float, required=True,  help="Height of the tessellation area.")
    parser.add_argument("--size",        type=float, required=True,  help="Circumradius of each hexagon.")
    parser.add_argument("--orientation", choices=["pointy", "flat"], default="pointy",
                        help="Hex orientation: pointy (default) or flat top.")
    parser.add_argument("--colormap",    default=None,
                        help="Matplotlib colormap for random-value coloring (e.g. viridis, plasma, coolwarm).")
    parser.add_argument("--output",      default=None,
                        help="Save plot to this file instead of displaying it (.png, .svg, .pdf).")
    args = parser.parse_args()

    grid = HexGrid(args.width, args.height, args.size, args.orientation)

    values = None
    if args.colormap:
        import random
        values = [random.random() for _ in grid]

    grid.plot(
        values=values,
        colormap=args.colormap or "viridis",
        output=args.output,
    )


if __name__ == "__main__":
    main()
