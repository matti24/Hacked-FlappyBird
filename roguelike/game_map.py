"""Karten-Datenstruktur: Tiles und das Dungeon-Raster."""

from __future__ import annotations


class Tile:
    """Ein einzelnes Feld der Karte."""

    __slots__ = ("walkable", "transparent", "explored")

    def __init__(self, walkable: bool, transparent: bool) -> None:
        self.walkable = walkable
        self.transparent = transparent
        # Wurde das Feld schon einmal gesehen? (für Fog of War)
        self.explored = False


def floor_tile() -> Tile:
    return Tile(walkable=True, transparent=True)


def wall_tile() -> Tile:
    return Tile(walkable=False, transparent=False)


class GameMap:
    """Ein Raster aus Tiles inklusive Sichtbarkeits-Status."""

    def __init__(self, width: int, height: int) -> None:
        self.width = width
        self.height = height
        # Standardmäßig alles Wand – die Generierung gräbt Räume frei.
        self.tiles: list[list[Tile]] = [
            [wall_tile() for _ in range(height)] for _ in range(width)
        ]
        # Aktuell sichtbare Felder (wird pro Runde neu berechnet).
        self.visible: set[tuple[int, int]] = set()
        # Position der Treppe zur nächsten Ebene.
        self.stairs_down: tuple[int, int] | None = None

    def in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height

    def is_walkable(self, x: int, y: int) -> bool:
        return self.in_bounds(x, y) and self.tiles[x][y].walkable

    def is_transparent(self, x: int, y: int) -> bool:
        return self.in_bounds(x, y) and self.tiles[x][y].transparent

    def set_tile(self, x: int, y: int, tile: Tile) -> None:
        if self.in_bounds(x, y):
            self.tiles[x][y] = tile

    def mark_explored(self, points: set[tuple[int, int]]) -> None:
        for (x, y) in points:
            if self.in_bounds(x, y):
                self.tiles[x][y].explored = True
