"""A*-Wegfindung auf dem Tile-Raster (4 Richtungen)."""

from __future__ import annotations

import heapq
import itertools

from .game_map import GameMap

_NEIGHBORS = ((0, -1), (0, 1), (-1, 0), (1, 0))


def _heuristic(a: tuple[int, int], b: tuple[int, int]) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def astar(
    game_map: GameMap,
    start: tuple[int, int],
    goal: tuple[int, int],
    blocked: set[tuple[int, int]] | None = None,
) -> list[tuple[int, int]]:
    """Kürzester Pfad von start nach goal.

    Gibt die Schritte OHNE den Startpunkt zurück (inkl. Ziel). Leere Liste,
    wenn kein Weg existiert. ``blocked`` markiert von anderen Wesen besetzte
    Felder; das Ziel selbst darf besetzt sein (z. B. der Spieler).
    """
    blocked = blocked or set()
    if start == goal:
        return []

    counter = itertools.count()
    open_heap: list[tuple[int, int, tuple[int, int]]] = [(0, next(counter), start)]
    came_from: dict[tuple[int, int], tuple[int, int]] = {}
    g_score: dict[tuple[int, int], int] = {start: 0}
    closed: set[tuple[int, int]] = set()

    while open_heap:
        _, _, current = heapq.heappop(open_heap)
        if current == goal:
            return _reconstruct(came_from, current)
        if current in closed:
            continue
        closed.add(current)

        cx, cy = current
        for dx, dy in _NEIGHBORS:
            nb = (cx + dx, cy + dy)
            if not game_map.is_walkable(*nb):
                continue
            if nb != goal and nb in blocked:
                continue
            tentative = g_score[current] + 1
            if tentative < g_score.get(nb, 1 << 30):
                came_from[nb] = current
                g_score[nb] = tentative
                f = tentative + _heuristic(nb, goal)
                heapq.heappush(open_heap, (f, next(counter), nb))

    return []


def _reconstruct(
    came_from: dict[tuple[int, int], tuple[int, int]],
    current: tuple[int, int],
) -> list[tuple[int, int]]:
    path = [current]
    while current in came_from:
        current = came_from[current]
        path.append(current)
    path.reverse()
    return path[1:]  # Startfeld weglassen
