"""Prozedurale Dungeon-Generierung: Räume platzieren und mit Gängen verbinden."""

from __future__ import annotations

import random

from .game_map import GameMap, floor_tile


class RectRoom:
    """Ein rechteckiger Raum, definiert über zwei Eckpunkte."""

    def __init__(self, x: int, y: int, width: int, height: int) -> None:
        self.x1 = x
        self.y1 = y
        self.x2 = x + width
        self.y2 = y + height

    @property
    def center(self) -> tuple[int, int]:
        return (self.x1 + self.x2) // 2, (self.y1 + self.y2) // 2

    def inner_tiles(self) -> list[tuple[int, int]]:
        """Alle begehbaren Felder im Inneren (mit 1 Feld Wandrand)."""
        return [
            (x, y)
            for x in range(self.x1 + 1, self.x2)
            for y in range(self.y1 + 1, self.y2)
        ]

    def intersects(self, other: "RectRoom") -> bool:
        return (
            self.x1 <= other.x2
            and self.x2 >= other.x1
            and self.y1 <= other.y2
            and self.y2 >= other.y1
        )


def _carve_room(game_map: GameMap, room: RectRoom) -> None:
    for (x, y) in room.inner_tiles():
        game_map.set_tile(x, y, floor_tile())


def _carve_h_tunnel(game_map: GameMap, x1: int, x2: int, y: int) -> None:
    for x in range(min(x1, x2), max(x1, x2) + 1):
        game_map.set_tile(x, y, floor_tile())


def _carve_v_tunnel(game_map: GameMap, y1: int, y2: int, x: int) -> None:
    for y in range(min(y1, y2), max(y1, y2) + 1):
        game_map.set_tile(x, y, floor_tile())


def _connect(game_map: GameMap, a: tuple[int, int], b: tuple[int, int], rng: random.Random) -> None:
    (x1, y1), (x2, y2) = a, b
    if rng.random() < 0.5:
        _carve_h_tunnel(game_map, x1, x2, y1)
        _carve_v_tunnel(game_map, y1, y2, x2)
    else:
        _carve_v_tunnel(game_map, y1, y2, x1)
        _carve_h_tunnel(game_map, x1, x2, y2)


def generate_dungeon(
    width: int,
    height: int,
    *,
    max_rooms: int,
    room_min_size: int,
    room_max_size: int,
    rng: random.Random | None = None,
) -> tuple[GameMap, list[RectRoom]]:
    """Erzeugt ein Dungeon und gibt Karte + platzierte Räume (in Reihenfolge) zurück."""
    rng = rng or random.Random()
    game_map = GameMap(width, height)
    rooms: list[RectRoom] = []

    for _ in range(max_rooms):
        w = rng.randint(room_min_size, room_max_size)
        h = rng.randint(room_min_size, room_max_size)
        x = rng.randint(0, width - w - 1)
        y = rng.randint(0, height - h - 1)
        new_room = RectRoom(x, y, w, h)

        if any(new_room.intersects(other) for other in rooms):
            continue

        _carve_room(game_map, new_room)
        if rooms:
            _connect(game_map, rooms[-1].center, new_room.center, rng)
        rooms.append(new_room)

    # Treppe nach unten im letzten (am weitesten entfernten) Raum.
    if rooms:
        game_map.stairs_down = rooms[-1].center

    return game_map, rooms
