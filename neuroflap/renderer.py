"""Darstellung der Simulation inkl. Live-Visualisierung des besten Netzes."""

from __future__ import annotations

import pygame

from . import config


class Renderer:
    def __init__(self) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode((config.WIDTH, config.HEIGHT))
        pygame.display.set_caption("NeuroFlap – KI lernt fliegen")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("consolas", 18)
        self.font_small = pygame.font.SysFont("consolas", 15)
        self.font_big = pygame.font.SysFont("consolas", 30, bold=True)
        self.font_label = pygame.font.SysFont("consolas", 13)
        self._background = self._make_background()

    def _make_background(self) -> pygame.Surface:
        surf = pygame.Surface((config.GAME_WIDTH, config.HEIGHT))
        top = config.COLOR_BG_TOP
        bottom = config.COLOR_BG_BOTTOM
        for y in range(config.HEIGHT):
            t = y / config.HEIGHT
            color = tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3))
            pygame.draw.line(surf, color, (0, y), (config.GAME_WIDTH, y))
        return surf

    def render(self, sim, speed: int) -> None:
        self.screen.blit(self._background, (0, 0))
        self._draw_pipes(sim)
        self._draw_birds(sim)
        self._draw_panel(sim, speed)
        pygame.display.flip()

    def _draw_pipes(self, sim) -> None:
        for pipe in sim.pipes:
            x = int(pipe.x)
            top_rect = (x, 0, config.PIPE_WIDTH, int(pipe.gap_top))
            bot_rect = (x, int(pipe.gap_bottom), config.PIPE_WIDTH, config.HEIGHT)
            pygame.draw.rect(self.screen, config.COLOR_PIPE, top_rect)
            pygame.draw.rect(self.screen, config.COLOR_PIPE, bot_rect)
            pygame.draw.rect(self.screen, config.COLOR_PIPE_EDGE, top_rect, 3)
            pygame.draw.rect(self.screen, config.COLOR_PIPE_EDGE, bot_rect, 3)

    def _draw_birds(self, sim) -> None:
        # Alle lebenden Vögel halbtransparent -> Schwarm-Effekt.
        layer = pygame.Surface((config.GAME_WIDTH, config.HEIGHT), pygame.SRCALPHA)
        best = sim.population.best_alive()
        for bird in sim.population.birds:
            if not bird.alive:
                continue
            pygame.draw.circle(
                layer, (*config.COLOR_BIRD, 70), (config.BIRD_X, int(bird.y)), config.BIRD_RADIUS
            )
        self.screen.blit(layer, (0, 0))

        if best is not None:
            pos = (config.BIRD_X, int(best.y))
            pygame.draw.circle(self.screen, config.COLOR_BIRD_BEST, pos, config.BIRD_RADIUS + 2)
            pygame.draw.circle(self.screen, (255, 255, 255), pos, config.BIRD_RADIUS + 2, 2)

    # ------------------------------------------------------------------
    # Rechtes Panel: Statistiken, Netz-Visualisierung, Fitness-Verlauf
    # ------------------------------------------------------------------
    def _draw_panel(self, sim, speed: int) -> None:
        px = config.GAME_WIDTH
        pygame.draw.rect(self.screen, config.COLOR_PANEL_BG, (px, 0, config.PANEL_WIDTH, config.HEIGHT))
        pygame.draw.line(self.screen, config.COLOR_ACCENT, (px, 0), (px, config.HEIGHT), 2)

        pop = sim.population
        alive = len(pop.alive_birds())
        cx = px + 20

        self.screen.blit(self.font_big.render("NeuroFlap", True, config.COLOR_TEXT), (cx, 18))
        self.screen.blit(
            self.font_small.render("KI lernt per Neuroevolution", True, config.COLOR_TEXT_DIM),
            (cx, 54),
        )

        rows = [
            ("Generation", f"{pop.generation}", config.COLOR_ACCENT_2),
            ("Vögel am Leben", f"{alive} / {config.POPULATION_SIZE}", config.COLOR_TEXT),
            ("Score aktuell", f"{sim.current_score()}", config.COLOR_TEXT),
            ("Bester Score", f"{pop.best_score_ever}", config.COLOR_BIRD_BEST),
            ("Beste Fitness", f"{int(pop.best_fitness_ever)}", config.COLOR_TEXT),
            ("Tempo", f"{speed}x", config.COLOR_ACCENT),
        ]
        y = 88
        for label, value, color in rows:
            self.screen.blit(self.font_small.render(label, True, config.COLOR_TEXT_DIM), (cx, y))
            val = self.font.render(value, True, color)
            self.screen.blit(val, (px + config.PANEL_WIDTH - 20 - val.get_width(), y - 2))
            y += 28

        self._draw_network(sim, px + 16, y + 6, config.PANEL_WIDTH - 32, 210)
        self._draw_fitness_graph(sim, px + 16, y + 250, config.PANEL_WIDTH - 32, 120)

        hint = "1-5 Tempo   P Pause   R Reset   Esc"
        self.screen.blit(
            self.font_label.render(hint, True, config.COLOR_TEXT_DIM),
            (cx, config.HEIGHT - 26),
        )

    def _draw_network(self, sim, x: int, y: int, w: int, h: int) -> None:
        self.screen.blit(self.font_small.render("Gehirn des Anführers", True, config.COLOR_TEXT_DIM), (x, y))
        top = y + 24
        area_h = h - 24

        best = sim.population.best_alive()
        brain = best.brain if best is not None else None

        layers = [config.INPUT_SIZE, config.HIDDEN_SIZE, config.OUTPUT_SIZE]
        activations = None
        if brain is not None:
            activations = [brain.last_input, brain.last_hidden, brain.last_output]

        # Knotenpositionen je Schicht berechnen.
        positions: list[list[tuple[int, int]]] = []
        for li, count in enumerate(layers):
            lx = x + int(w * (li / (len(layers) - 1))) if len(layers) > 1 else x
            lx = min(max(lx, x + 14), x + w - 14)
            col = []
            for n in range(count):
                ny = top + int(area_h * ((n + 0.5) / count))
                col.append((lx, ny))
            positions.append(col)

        # Kanten (Gewichte) zeichnen.
        if brain is not None:
            self._draw_edges(positions[0], positions[1], brain.w1)
            self._draw_edges(positions[1], positions[2], brain.w2)

        # Knoten zeichnen, Helligkeit nach Aktivierung.
        for li, col in enumerate(positions):
            for n, (nx, ny) in enumerate(col):
                act = 0.0
                if activations is not None:
                    act = abs(activations[li][n]) if n < len(activations[li]) else 0.0
                shade = min(255, int(70 + act * 185))
                color = (shade, shade, min(255, shade + 30))
                pygame.draw.circle(self.screen, color, (nx, ny), 8)
                pygame.draw.circle(self.screen, config.COLOR_NODE, (nx, ny), 8, 1)

    def _draw_edges(self, src, dst, weights) -> None:
        for j, (dx, dy) in enumerate(dst):
            row = weights[j] if j < len(weights) else []
            for i, (sx, sy) in enumerate(src):
                if i >= len(row):
                    continue
                weight = row[i]
                color = config.COLOR_EDGE_POS if weight >= 0 else config.COLOR_EDGE_NEG
                width = max(1, min(4, int(abs(weight) * 1.5)))
                pygame.draw.line(self.screen, color, (sx, sy), (dx, dy), width)

    def _draw_fitness_graph(self, sim, x: int, y: int, w: int, h: int) -> None:
        self.screen.blit(self.font_small.render("Beste Fitness je Generation", True, config.COLOR_TEXT_DIM), (x, y))
        gy = y + 22
        gh = h - 22
        pygame.draw.rect(self.screen, (10, 12, 24), (x, gy, w, gh))
        pygame.draw.rect(self.screen, config.COLOR_NODE, (x, gy, w, gh), 1)

        history = sim.population.fitness_history
        if len(history) < 2:
            return
        peak = max(history) or 1.0
        points = []
        n = len(history)
        for i, value in enumerate(history):
            hx = x + int(w * (i / (n - 1)))
            hy = gy + gh - int(gh * (value / peak))
            points.append((hx, hy))
        pygame.draw.lines(self.screen, config.COLOR_ACCENT_2, False, points, 2)
