"""Röhrenpaare, die von rechts nach links scrollen."""

from __future__ import annotations

from . import config


class Pipe:
    def __init__(self, x: float, gap_y: float) -> None:
        self.x = x
        self.gap_y = gap_y      # vertikale Mitte der Lücke
        self.scored = False     # wurde diese Röhre bereits gezählt?

    @property
    def gap_top(self) -> float:
        return self.gap_y - config.PIPE_GAP / 2

    @property
    def gap_bottom(self) -> float:
        return self.gap_y + config.PIPE_GAP / 2

    def update(self) -> None:
        self.x -= config.PIPE_SPEED

    def is_offscreen(self) -> bool:
        return self.x + config.PIPE_WIDTH < 0

    def collides_with(self, bird_y: float) -> bool:
        bx = config.BIRD_X
        r = config.BIRD_RADIUS
        # Horizontale Überlappung mit dem Vogel?
        if bx + r < self.x or bx - r > self.x + config.PIPE_WIDTH:
            return False
        # Vertikal außerhalb der Lücke -> Treffer.
        return bird_y - r < self.gap_top or bird_y + r > self.gap_bottom
