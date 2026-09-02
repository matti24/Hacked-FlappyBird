"""Gegner-KI als Zustandsautomat.

Zustände:
- ``wander``: ziellos umherstreifen, bis der Spieler gesichtet wird.
- ``chase``: den Spieler per A* verfolgen; bei Nachbarschaft angreifen.
  Verliert der Gegner den Spieler aus den Augen, verfolgt er noch einige
  Runden die zuletzt bekannte Position, bevor er wieder umherstreift.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .config import ENEMY_MEMORY_TURNS, FOV_RADIUS
from .pathfinding import astar

if TYPE_CHECKING:
    from .entities import Actor
    from .game import Game

_ORTHOGONAL = ((0, -1), (0, 1), (-1, 0), (1, 0))


def _has_line_of_sight(game_map, start: tuple[int, int], end: tuple[int, int]) -> bool:
    """Bresenham-Sichtlinie: True, wenn keine Wand dazwischen liegt."""
    x0, y0 = start
    x1, y1 = end
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy
    x, y = x0, y0
    while (x, y) != (x1, y1):
        if (x, y) != start and not game_map.is_transparent(x, y):
            return False
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x += sx
        if e2 < dx:
            err += dx
            y += sy
    return True


class HostileAI:
    def __init__(self) -> None:
        self.state = "wander"
        self.last_known: tuple[int, int] | None = None
        self.memory = 0

    def can_see_player(self, actor: "Actor", game: "Game") -> bool:
        player = game.player
        if actor.distance_to(player) > FOV_RADIUS:
            return False
        return _has_line_of_sight(game.game_map, actor.pos, player.pos)

    def take_turn(self, actor: "Actor", game: "Game") -> None:
        player = game.player

        if self.can_see_player(actor, game):
            self.state = "chase"
            self.last_known = player.pos
            self.memory = ENEMY_MEMORY_TURNS

            # Orthogonal benachbart -> angreifen statt bewegen.
            if abs(actor.x - player.x) + abs(actor.y - player.y) == 1:
                game.enemy_attack(actor, player)
            else:
                self._step_towards(actor, player.pos, game)
            return

        # Spieler nicht in Sicht: der zuletzt bekannten Position nachgehen.
        if self.memory > 0 and self.last_known is not None:
            self.memory -= 1
            if actor.pos == self.last_known:
                self.last_known = None
                self.memory = 0
                self.state = "wander"
            else:
                self.state = "chase"
                self._step_towards(actor, self.last_known, game)
            return

        self.state = "wander"
        self._wander(actor, game)

    def _step_towards(self, actor: "Actor", target: tuple[int, int], game: "Game") -> None:
        blocked = game.blocking_positions(exclude=actor)
        path = astar(game.game_map, actor.pos, target, blocked)
        if not path:
            return
        step = path[0]
        if step != game.player.pos and step not in blocked:
            actor.pos = step

    def _wander(self, actor: "Actor", game: "Game") -> None:
        # Meistens stehen bleiben, gelegentlich einen Schritt gehen.
        if game.rng.random() < 0.6:
            return
        blocked = game.blocking_positions(exclude=actor)
        game.rng.shuffle(dirs := list(_ORTHOGONAL))
        for dx, dy in dirs:
            nx, ny = actor.x + dx, actor.y + dy
            if (
                game.game_map.is_walkable(nx, ny)
                and (nx, ny) not in blocked
                and (nx, ny) != game.player.pos
            ):
                actor.pos = (nx, ny)
                return
