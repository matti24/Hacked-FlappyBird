"""Sichtfeldberechnung per Recursive Shadowcasting.

Bestimmt, welche Felder von einem Ursprung aus sichtbar sind – inklusive
korrekter Schattenwürfe hinter Wänden. Reine Logik, unabhängig von pygame.
"""

from __future__ import annotations

from .game_map import GameMap

# Transformationsmatrix für die 8 Oktanten.
_MULT = (
    (1, 0, 0, -1, -1, 0, 0, 1),
    (0, 1, -1, 0, 0, -1, 1, 0),
    (0, 1, 1, 0, 0, -1, -1, 0),
    (1, 0, 0, 1, -1, 0, 0, -1),
)


def _cast_light(
    game_map: GameMap,
    cx: int,
    cy: int,
    row: int,
    start_slope: float,
    end_slope: float,
    radius: int,
    xx: int,
    xy: int,
    yx: int,
    yy: int,
    visible: set[tuple[int, int]],
) -> None:
    if start_slope < end_slope:
        return

    radius_sq = radius * radius
    new_start = start_slope

    for j in range(row, radius + 1):
        dx, dy = -j - 1, -j
        blocked = False

        while dx <= 0:
            dx += 1
            map_x = cx + dx * xx + dy * xy
            map_y = cy + dx * yx + dy * yy
            l_slope = (dx - 0.5) / (dy + 0.5)
            r_slope = (dx + 0.5) / (dy - 0.5)

            if start_slope < r_slope:
                continue
            if end_slope > l_slope:
                break

            if dx * dx + dy * dy <= radius_sq and game_map.in_bounds(map_x, map_y):
                visible.add((map_x, map_y))

            if blocked:
                if not game_map.is_transparent(map_x, map_y):
                    new_start = r_slope
                    continue
                blocked = False
                start_slope = new_start
            elif not game_map.is_transparent(map_x, map_y) and j < radius:
                blocked = True
                _cast_light(
                    game_map, cx, cy, j + 1, start_slope, l_slope, radius,
                    xx, xy, yx, yy, visible,
                )
                new_start = r_slope

        if blocked:
            break


def compute_fov(game_map: GameMap, origin: tuple[int, int], radius: int) -> set[tuple[int, int]]:
    """Gibt die Menge der sichtbaren Felder vom Ursprung aus zurück."""
    cx, cy = origin
    visible: set[tuple[int, int]] = {(cx, cy)}
    for octant in range(8):
        _cast_light(
            game_map, cx, cy, 1, 1.0, 0.0, radius,
            _MULT[0][octant], _MULT[1][octant], _MULT[2][octant], _MULT[3][octant],
            visible,
        )
    return visible
