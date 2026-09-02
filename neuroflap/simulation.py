"""Simulation: Physik, Fitness, Röhren-Verwaltung und Hauptschleife."""

from __future__ import annotations

import random

from . import config
from .pipe import Pipe
from .population import Population


class Simulation:
    def __init__(self, rng: random.Random | None = None) -> None:
        self.rng = rng or random.Random()
        self.population = Population(self.rng)
        self.pipes: list[Pipe] = []
        self.frame = 0
        self._active_pipes = config.GAME_WIDTH // config.PIPE_SPACING + 2
        self.reset_round()

    # ------------------------------------------------------------------
    # Röhren
    # ------------------------------------------------------------------
    def _random_gap_y(self) -> float:
        lo = config.PIPE_MIN_MARGIN + config.PIPE_GAP / 2
        hi = config.HEIGHT - config.PIPE_MIN_MARGIN - config.PIPE_GAP / 2
        return self.rng.uniform(lo, hi)

    def _add_pipe(self) -> None:
        if self.pipes:
            x = self.pipes[-1].x + config.PIPE_SPACING
        else:
            x = config.GAME_WIDTH
        self.pipes.append(Pipe(x, self._random_gap_y()))

    def reset_round(self) -> None:
        self.pipes = []
        while len(self.pipes) < self._active_pipes:
            self._add_pipe()
        self.frame = 0

    def _next_pipe(self) -> Pipe | None:
        for pipe in self.pipes:
            if pipe.x + config.PIPE_WIDTH >= config.BIRD_X:
                return pipe
        return self.pipes[-1] if self.pipes else None

    def _inputs_for(self, bird, pipe: Pipe) -> list[float]:
        return [
            bird.y / config.HEIGHT,
            bird.velocity / 10.0,
            (pipe.x - config.BIRD_X) / config.GAME_WIDTH,
            (pipe.gap_top - bird.y) / config.HEIGHT,
            (pipe.gap_bottom - bird.y) / config.HEIGHT,
        ]

    def current_score(self) -> int:
        return max((b.score for b in self.population.birds), default=0)

    # ------------------------------------------------------------------
    # Ein Simulationsschritt
    # ------------------------------------------------------------------
    def step(self) -> None:
        pipe = self._next_pipe()

        for bird in self.population.birds:
            if not bird.alive:
                continue
            if pipe is not None:
                bird.decide(self._inputs_for(bird, pipe))
            bird.update()
            bird.fitness += 1

            if bird.y - config.BIRD_RADIUS < 0 or bird.y + config.BIRD_RADIUS > config.HEIGHT:
                bird.alive = False
                continue
            for p in self.pipes:
                if p.collides_with(bird.y):
                    bird.alive = False
                    break

        for p in self.pipes:
            p.update()

        # Punkte vergeben, sobald eine Röhre den Vogel passiert hat.
        for p in self.pipes:
            if not p.scored and p.x + config.PIPE_WIDTH < config.BIRD_X:
                p.scored = True
                for bird in self.population.birds:
                    if bird.alive:
                        bird.score += 1
                        bird.fitness += 25

        self.pipes = [p for p in self.pipes if not p.is_offscreen()]
        while len(self.pipes) < self._active_pipes:
            self._add_pipe()

        self.frame += 1

        if self.population.all_dead():
            self.population.evolve()
            self.reset_round()


# ----------------------------------------------------------------------
# Hauptschleife
# ----------------------------------------------------------------------
def main() -> None:
    import pygame

    from .renderer import Renderer

    speeds = {
        pygame.K_1: 1,
        pygame.K_2: 2,
        pygame.K_3: 4,
        pygame.K_4: 8,
        pygame.K_5: 30,
    }

    renderer = Renderer()
    sim = Simulation()
    speed = 2
    paused = False
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_p:
                    paused = not paused
                elif event.key == pygame.K_r:
                    sim = Simulation()
                elif event.key in speeds:
                    speed = speeds[event.key]

        if not paused:
            for _ in range(speed):
                sim.step()

        renderer.render(sim, speed)
        renderer.clock.tick(config.FPS)

    pygame.quit()
