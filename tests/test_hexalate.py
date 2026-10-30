"""Smoke tests for hexalate."""

import pytest

import hexalate as hx


def test_hexagon_vertices() -> None:
    vertices = hx.hexagon(0, 0, 1.0)
    assert len(vertices) == 7
    assert vertices[0] == pytest.approx(vertices[-1])


def test_hexgrid_iterates_and_accesses() -> None:
    grid = hx.HexGrid(width=5, height=4, hex_size=0.5)
    hexagons = list(grid)
    assert len(hexagons) > 0
    first = hexagons[0]
    fetched = grid.get(first.q, first.r)
    assert fetched is not None
    assert fetched.q == first.q
    assert fetched.r == first.r


def test_neighbor_and_distance() -> None:
    grid = hx.HexGrid(width=5, height=4, hex_size=0.5)
    h = grid.get(0, 0)
    assert h is not None
    assert len(h.neighbor_coords()) == 6
    assert h.distance_to(h) == 0


def test_hexagon_serialization() -> None:
    grid = hx.HexGrid(width=5, height=4, hex_size=0.5)
    h = list(grid)[0]
    data = h.to_dict()
    assert data["q"] == h.q
    assert data["r"] == h.r
    assert len(data["coords"]) == 7
