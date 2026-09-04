"""Simulation: Physik, Fitness, progressive Schwierigkeit, KI- und Mensch-Modus."""

from __future__ import annotations

import random

import pygame

from . import config
from .bird import Bird
from .pipe import Pipe
from .population import Population


class Simulation:
    def __init__(self, rng: random.Random | None = None) -> None:
        self.rng = rng or random.Random()
        self.population = Population(self.rng)
        self.pipes: list[Pipe] = []
        self.frame = 0
        self._active_pipes = config.GAME_WIDTH // config.PIPE_SPACING + 2

        # Mensch-Modus
        self.mode = "ai"                 # "ai" oder "human"
        self.player: Bird | None = None
        self.human_score = 0
        self.human_best = 0
        self.human_dead = False

        self.reset_round()

    # ------------------------------------------------------------------
    # Schwierigkeit steigt mit dem Score
    # ------------------------------------------------------------------
    def difficulty_speed(self, score: int) -> float:
        return config.PIPE_SPEED + min(score * config.DIFF_SPEED_PER_SCORE, config.PIPE_SPEED_MAX_BONUS)

    def difficulty_gap(self, score: int) -> float:
        return max(config.PIPE_GAP_MIN, config.PIPE_GAP - score * config.DIFF_GAP_PER_SCORE)

    # ------------------------------------------------------------------
    # Röhren
    # ------------------------------------------------------------------
    def _random_gap_y(self, gap_size: float) -> float:
        lo = config.PIPE_MIN_MARGIN + gap_size / 2
        hi = config.HEIGHT - config.PIPE_MIN_MARGIN - gap_size / 2
        return self.rng.uniform(lo, hi)

    def _add_pipe(self, gap_size: float) -> None:
        x = self.pipes[-1].x + config.PIPE_SPACING if self.pipes else config.GAME_WIDTH
        self.pipes.append(Pipe(x, self._random_gap_y(gap_size), gap_size))

    def reset_round(self) -> None:
        self.pipes = []
        gap = self.difficulty_gap(0)
        while len(self.pipes) < self._active_pipes:
            self._add_pipe(gap)
        self.frame = 0

    def _next_pipe(self) -> Pipe | None:
        for pipe in self.pipes:
            if pipe.x + config.PIPE_WIDTH >= config.BIRD_X:
                return pipe
        return self.pipes[-1] if self.pipes else None

    def _inputs_for(self, bird: Bird, pipe: Pipe) -> list[float]:
        return [
            bird.y / config.HEIGHT,
            bird.velocity / 10.0,
            (pipe.x - config.BIRD_X) / config.GAME_WIDTH,
            (pipe.gap_top - bird.y) / config.HEIGHT,
            (pipe.gap_bottom - bird.y) / config.HEIGHT,
        ]

    def current_score(self) -> int:
        if self.mode == "human":
            return self.human_score
        return max((b.score for b in self.population.birds), default=0)

    # ------------------------------------------------------------------
    # Schritt (verzweigt nach Modus)
    # ------------------------------------------------------------------
    def step(self) -> None:
        if self.mode == "human":
            self._step_human()
        else:
            self._step_ai()

    def _step_ai(self) -> None:
        score = self.current_score()
        speed = self.difficulty_speed(score)
        pipe = self._next_pipe()
        r = config.BIRD_RADIUS

        for bird in self.population.birds:
            if not bird.alive:
                continue
            if pipe is not None:
                bird.decide(self._inputs_for(bird, pipe))
            bird.update()
            bird.fitness += 1.0
            if pipe is not None:
                # Zentrales Durchfliegen der Lücke belohnen (glatter Gradient).
                closeness = max(0.0, 1.0 - abs(bird.y - pipe.gap_y) / (pipe.gap_size / 2.0))
                bird.fitness += closeness * config.FITNESS_CENTER_BONUS
            if bird.y - r < 0 or bird.y + r > config.HEIGHT:
                bird.alive = False
                continue
            for p in self.pipes:
                if p.collides_with(bird.y):
                    bird.alive = False
                    break

        for p in self.pipes:
            p.update(speed)

        for p in self.pipes:
            if not p.scored and p.x + config.PIPE_WIDTH < config.BIRD_X:
                p.scored = True
                for bird in self.population.birds:
                    if bird.alive:
                        bird.score += 1
                        bird.fitness += config.FITNESS_PIPE_BONUS

        cur = self.current_score()
        self._recycle_pipes(cur)
        if cur > self.population.best_score_ever:
            self.population.best_score_ever = cur
        self.frame += 1

        # Alle tot ODER Sicherheits-Limit erreicht -> nächste Generation.
        if self.population.all_dead() or self.frame >= config.MAX_ROUND_FRAMES:
            self.population.evolve()
            self.reset_round()

    def _step_human(self) -> None:
        if self.human_dead or self.player is None:
            return
        speed = self.difficulty_speed(self.human_score)
        r = config.BIRD_RADIUS

        self.player.update()
        if self.player.y - r < 0 or self.player.y + r > config.HEIGHT:
            self._end_human_round()
            return
        for p in self.pipes:
            if p.collides_with(self.player.y):
                self._end_human_round()
                return

        for p in self.pipes:
            p.update(speed)
        for p in self.pipes:
            if not p.scored and p.x + config.PIPE_WIDTH < config.BIRD_X:
                p.scored = True
                self.human_score += 1

        self._recycle_pipes(self.human_score)
        self.frame += 1

    def _recycle_pipes(self, score: int) -> None:
        self.pipes = [p for p in self.pipes if not p.is_offscreen()]
        while len(self.pipes) < self._active_pipes:
            self._add_pipe(self.difficulty_gap(score))

    # ------------------------------------------------------------------
    # Modus-Wechsel & Spieler
    # ------------------------------------------------------------------
    def set_mode(self, mode: str) -> None:
        if mode == self.mode:
            return
        self.mode = mode
        if mode == "human":
            self._start_human_round()
        else:
            self.reset_round()

    def _start_human_round(self) -> None:
        self.player = Bird(None)
        self.player.y = config.HEIGHT / 2
        self.human_score = 0
        self.human_dead = False
        self.reset_round()

    def player_flap(self) -> None:
        if self.mode != "human":
            return
        if self.human_dead:
            self._start_human_round()
        elif self.player is not None:
            self.player.flap()

    def _end_human_round(self) -> None:
        self.human_dead = True
        self.human_best = max(self.human_best, self.human_score)


# ----------------------------------------------------------------------
# Hauptschleife
# ----------------------------------------------------------------------
async def main() -> None:
    import asyncio

    pygame.init()  # pygbag/WASM: Subsysteme + Konstanten verfügbar machen

    from .renderer import Renderer

    speeds = {pygame.K_1: 1, pygame.K_2: 2, pygame.K_3: 4, pygame.K_4: 8, pygame.K_5: 30}
    flap_keys = {pygame.K_SPACE, pygame.K_UP, pygame.K_w}

    renderer = Renderer()
    sim = Simulation()
    speed = 1
    active = True
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if renderer.mode_rect.collidepoint(event.pos):
                    sim.set_mode("human" if sim.mode == "ai" else "ai")
                elif sim.mode == "ai" and renderer.toggle_rect.collidepoint(event.pos):
                    active = not active
                elif sim.mode == "human":
                    sim.player_flap()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_m:
                    sim.set_mode("human" if sim.mode == "ai" else "ai")
                elif event.key == pygame.K_r:
                    if sim.mode == "human":
                        sim._start_human_round()
                    else:
                        sim = Simulation()
                elif sim.mode == "human" and event.key in flap_keys:
                    sim.player_flap()
                elif sim.mode == "ai":
                    if event.key in (pygame.K_SPACE, pygame.K_p):
                        active = not active
                    elif event.key in speeds:
                        speed = speeds[event.key]

        if sim.mode == "ai":
            if active:
                for _ in range(speed):
                    sim.step()
        else:
            sim.step()

        renderer.render(sim, speed, active)
        renderer.clock.tick(config.FPS)
        await asyncio.sleep(0)  # Kontrolle an den Browser zurückgeben (pygbag)

    pygame.quit()
