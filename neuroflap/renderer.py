"""Darstellung der Simulation mit aufwändigem UI und Netz-Visualisierung."""

from __future__ import annotations

import math
import random

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

        self._bg = self._make_gradient()

        rng = random.Random(42)
        # Sterne: (x, y, größe, twinkle-phase, drift-tempo)
        self.stars = [
            (
                rng.uniform(0, config.GAME_WIDTH),
                rng.uniform(0, config.HEIGHT),
                rng.uniform(0.6, 2.1),
                rng.uniform(0, math.tau),
                rng.uniform(6, 22),
            )
            for _ in range(config.STAR_COUNT)
        ]
        # Nebel: vorgerenderte weiche Glow-Flächen
        self.nebulae = [
            (self._radial_glow(230, config.COLOR_NEBULA_A, 46), 150, 180, 18.0),
            (self._radial_glow(200, config.COLOR_NEBULA_B, 40), 560, 520, 24.0),
        ]

        self._bird_glow = self._radial_glow(int(config.BIRD_RADIUS * 2.3), config.COLOR_BIRD_GLOW, 60)
        self._leader_aura = self._radial_glow(config.BIRD_RADIUS * 4, config.COLOR_LEADER_AURA, 150)

        # Klickbereich des An/Aus-Schalters (wird beim Zeichnen aktualisiert).
        self.toggle_rect = pygame.Rect(config.GAME_WIDTH + 18, 82, config.PANEL_WIDTH - 36, 40)
        self._trail: list[tuple[float, float]] = []

    # ------------------------------------------------------------------
    # Hilfssurfaces
    # ------------------------------------------------------------------
    def _make_gradient(self) -> pygame.Surface:
        surf = pygame.Surface((config.GAME_WIDTH, config.HEIGHT))
        top, bottom = config.COLOR_BG_TOP, config.COLOR_BG_BOTTOM
        for y in range(config.HEIGHT):
            t = y / config.HEIGHT
            color = tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3))
            pygame.draw.line(surf, color, (0, y), (config.GAME_WIDTH, y))
        return surf

    def _radial_glow(self, radius: int, color: tuple[int, int, int], max_alpha: int) -> pygame.Surface:
        surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        for r in range(radius, 0, -1):
            alpha = int(max_alpha * (1 - r / radius) ** 2)
            if alpha <= 0:
                continue
            pygame.draw.circle(surf, (*color, alpha), (radius, radius), r)
        return surf

    # ------------------------------------------------------------------
    # Haupt-Render
    # ------------------------------------------------------------------
    def render(self, sim, speed: int, active: bool = True) -> None:
        t = pygame.time.get_ticks() / 1000.0
        self._draw_background(t)
        self._draw_pipes(sim, t)
        self._draw_birds(sim, t)
        self._draw_panel(sim, speed, active, t)
        pygame.display.flip()

    def _draw_background(self, t: float) -> None:
        self.screen.blit(self._bg, (0, 0))

        # Driftende Nebelschwaden.
        for surf, bx, by, speed in self.nebulae:
            dx = (bx - t * speed) % (config.GAME_WIDTH + 460) - 230
            self.screen.blit(surf, (dx, by - surf.get_height() / 2), special_flags=pygame.BLEND_ADD)

        # Dezentes, scrollendes Gitter (Tech-Look).
        offset = int(t * 26) % 48
        for gx in range(-offset, config.GAME_WIDTH, 48):
            pygame.draw.line(self.screen, config.COLOR_GRID, (gx, 0), (gx, config.HEIGHT), 1)
        for gy in range(0, config.HEIGHT, 48):
            pygame.draw.line(self.screen, config.COLOR_GRID, (0, gy), (config.GAME_WIDTH, gy), 1)

        # Funkelnde, langsam driftende Sterne.
        for (sx, sy, size, phase, drift) in self.stars:
            x = (sx - t * drift) % config.GAME_WIDTH
            twinkle = 0.5 + 0.5 * math.sin(t * 2.2 + phase)
            shade = int(120 + 135 * twinkle)
            pygame.draw.circle(self.screen, (shade, shade, min(255, shade + 40)), (int(x), int(sy)), max(1, int(size)))

    def _draw_pipes(self, sim, t: float) -> None:
        pulse = 0.5 + 0.5 * math.sin(t * 4.0)
        for pipe in sim.pipes:
            x = int(pipe.x)
            w = config.PIPE_WIDTH
            top_h = int(pipe.gap_top)
            bot_y = int(pipe.gap_bottom)

            # Weicher Glow hinter der Röhre.
            glow = pygame.Surface((w + 24, config.HEIGHT), pygame.SRCALPHA)
            glow.fill((*config.COLOR_PIPE_GLOW, 24))
            self.screen.blit(glow, (x - 12, 0), special_flags=pygame.BLEND_ADD)

            self._draw_pipe_body(x, 0, w, top_h)
            self._draw_pipe_body(x, bot_y, w, config.HEIGHT - bot_y)

            # Leuchtende Kappen an den Lückenkanten (pulsierend).
            cap_color = tuple(int(config.COLOR_PIPE_CAP[i] * (0.7 + 0.3 * pulse)) for i in range(3))
            pygame.draw.rect(self.screen, cap_color, (x - 4, top_h - 14, w + 8, 14), border_radius=5)
            pygame.draw.rect(self.screen, cap_color, (x - 4, bot_y, w + 8, 14), border_radius=5)

    def _draw_pipe_body(self, x: int, y: int, w: int, h: int) -> None:
        if h <= 0:
            return
        # Horizontaler Verlauf für plastische Wirkung.
        body = pygame.Surface((w, h))
        core, glow = config.COLOR_PIPE_CORE, config.COLOR_PIPE_GLOW
        for col in range(w):
            f = 1 - abs(col - w / 2) / (w / 2)
            shade = tuple(int(core[i] + (glow[i] - core[i]) * f * 0.55) for i in range(3))
            pygame.draw.line(body, shade, (col, 0), (col, h))
        self.screen.blit(body, (x, y))
        pygame.draw.rect(self.screen, config.COLOR_PIPE_CAP, (x, y, w, h), 2)

    def _draw_birds(self, sim, t: float) -> None:
        best = sim.population.best_alive()

        # Schwarm als additiv glühende Wolke.
        glow_layer = pygame.Surface((config.GAME_WIDTH, config.HEIGHT), pygame.SRCALPHA)
        gw = self._bird_glow.get_width() / 2
        for bird in sim.population.birds:
            if bird.alive and bird is not best:
                glow_layer.blit(self._bird_glow, (config.BIRD_X - gw, bird.y - gw))
        self.screen.blit(glow_layer, (0, 0), special_flags=pygame.BLEND_ADD)

        if best is not None:
            self._draw_leader(best, t)

    def _draw_leader(self, bird, t: float) -> None:
        pos = (config.BIRD_X, int(bird.y))

        # Goldene Aura.
        ar = self._leader_aura.get_width() / 2
        self.screen.blit(self._leader_aura, (pos[0] - ar, pos[1] - ar), special_flags=pygame.BLEND_ADD)

        # Kurzer Schweif.
        self._trail.append((float(pos[0]), float(pos[1])))
        if len(self._trail) > 14:
            self._trail.pop(0)
        for i, (tx, ty) in enumerate(self._trail[:-1]):
            alpha = int(120 * (i / len(self._trail)))
            r = max(1, int(config.BIRD_RADIUS * 0.5 * (i / len(self._trail))))
            dot = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
            pygame.draw.circle(dot, (*config.COLOR_BIRD_BEST, alpha), (r, r), r)
            self.screen.blit(dot, (tx - r, ty - r), special_flags=pygame.BLEND_ADD)

        # Vogel auf eigene Surface zeichnen und nach Geschwindigkeit neigen.
        size = config.BIRD_RADIUS * 4
        s = pygame.Surface((size, size), pygame.SRCALPHA)
        cx = cy = size // 2
        r = config.BIRD_RADIUS + 1
        pygame.draw.circle(s, config.COLOR_BIRD_BEST, (cx, cy), r)
        pygame.draw.circle(s, (255, 255, 255), (cx, cy), r, 2)
        # schlagender Flügel
        wing = math.sin(t * 16) * 4
        pygame.draw.ellipse(s, config.COLOR_BIRD_WING, (cx - 11, cy - 2 + wing, 13, 9))
        # Auge + Pupille
        pygame.draw.circle(s, (255, 255, 255), (cx + 5, cy - 4), 3)
        pygame.draw.circle(s, (18, 18, 30), (cx + 6, cy - 4), 1)
        # Schnabel
        pygame.draw.polygon(s, (250, 175, 60), [(cx + r, cy), (cx + r + 8, cy - 2), (cx + r + 8, cy + 3)])

        angle = max(-32, min(65, -bird.velocity * 4.5))
        rotated = pygame.transform.rotate(s, angle)
        self.screen.blit(rotated, rotated.get_rect(center=pos))

    # ------------------------------------------------------------------
    # Panel
    # ------------------------------------------------------------------
    def _draw_panel(self, sim, speed: int, active: bool, t: float) -> None:
        px = config.GAME_WIDTH
        pygame.draw.rect(self.screen, config.COLOR_PANEL_BG, (px, 0, config.PANEL_WIDTH, config.HEIGHT))
        pygame.draw.line(self.screen, config.COLOR_ACCENT, (px, 0), (px, config.HEIGHT), 2)
        cx = px + 20

        self.screen.blit(self.font_big.render("NeuroFlap", True, config.COLOR_TEXT), (cx, 16))
        self.screen.blit(
            self.font_small.render("KI lernt per Neuroevolution", True, config.COLOR_TEXT_DIM),
            (cx, 50),
        )

        self._draw_toggle(px, 82, active)

        pop = sim.population
        rows = [
            ("Generation", f"{pop.generation}", config.COLOR_ACCENT_2),
            ("Vögel am Leben", f"{len(pop.alive_birds())} / {config.POPULATION_SIZE}", config.COLOR_TEXT),
            ("Score aktuell", f"{sim.current_score()}", config.COLOR_TEXT),
            ("Bester Score", f"{pop.best_score_ever}", config.COLOR_BIRD_BEST),
            ("Beste Fitness", f"{int(pop.best_fitness_ever)}", config.COLOR_TEXT),
            ("Tempo", f"{speed}x", config.COLOR_ACCENT),
        ]
        y = 140
        for label, value, color in rows:
            self.screen.blit(self.font_small.render(label, True, config.COLOR_TEXT_DIM), (cx, y))
            val = self.font.render(value, True, color)
            self.screen.blit(val, (px + config.PANEL_WIDTH - 20 - val.get_width(), y - 2))
            y += 25

        self._draw_network(sim, px + 16, y + 6, config.PANEL_WIDTH - 32, 196)
        self._draw_fitness_graph(sim, px + 16, y + 232, config.PANEL_WIDTH - 32, 110)

        hint = "Klick/Leertaste: An/Aus   1-5 Tempo   R Reset   Esc"
        self.screen.blit(self.font_label.render(hint, True, config.COLOR_TEXT_DIM), (cx, config.HEIGHT - 24))

    def _draw_toggle(self, px: int, y: int, active: bool) -> None:
        card = pygame.Rect(px + 18, y, config.PANEL_WIDTH - 36, 40)
        self.toggle_rect = card
        pygame.draw.rect(self.screen, config.COLOR_CARD_BG, card, border_radius=10)
        border = config.COLOR_ACCENT if active else config.COLOR_TOGGLE_OFF
        pygame.draw.rect(self.screen, border, card, 1, border_radius=10)

        label = "Simulation läuft" if active else "Simulation pausiert"
        self.screen.blit(self.font_small.render(label, True, config.COLOR_TEXT), (card.x + 12, card.y + 12))

        # Switch (Pill + Knopf) rechts in der Karte.
        sw_w, sw_h = 48, 24
        sx = card.right - sw_w - 12
        sy = card.y + (card.height - sw_h) // 2
        track = config.COLOR_TOGGLE_ON if active else config.COLOR_TOGGLE_OFF
        pygame.draw.rect(self.screen, track, (sx, sy, sw_w, sw_h), border_radius=12)
        knob_x = sx + sw_w - sw_h // 2 - 2 if active else sx + sw_h // 2 + 2
        pygame.draw.circle(self.screen, config.COLOR_TOGGLE_KNOB, (knob_x, sy + sw_h // 2), sw_h // 2 - 3)

    def _draw_network(self, sim, x: int, y: int, w: int, h: int) -> None:
        self.screen.blit(self.font_small.render("Gehirn des Anführers", True, config.COLOR_TEXT_DIM), (x, y))
        top = y + 22
        area_h = h - 22

        best = sim.population.best_alive()
        brain = best.brain if best is not None else None
        layers = [config.INPUT_SIZE, config.HIDDEN_SIZE, config.OUTPUT_SIZE]
        activations = None
        if brain is not None:
            activations = [brain.last_input, brain.last_hidden, brain.last_output]

        positions: list[list[tuple[int, int]]] = []
        for li, count in enumerate(layers):
            lx = x + int(w * (li / (len(layers) - 1)))
            lx = min(max(lx, x + 14), x + w - 14)
            positions.append([(lx, top + int(area_h * ((n + 0.5) / count))) for n in range(count)])

        if brain is not None:
            self._draw_edges(positions[0], positions[1], brain.w1)
            self._draw_edges(positions[1], positions[2], brain.w2)

        for li, col in enumerate(positions):
            for n, (nx, ny) in enumerate(col):
                act = abs(activations[li][n]) if activations and n < len(activations[li]) else 0.0
                shade = min(255, int(70 + act * 185))
                pygame.draw.circle(self.screen, (shade, shade, min(255, shade + 30)), (nx, ny), 8)
                pygame.draw.circle(self.screen, config.COLOR_NODE, (nx, ny), 8, 1)

    def _draw_edges(self, src, dst, weights) -> None:
        for j, (dx, dy) in enumerate(dst):
            row = weights[j] if j < len(weights) else []
            for i, (sx, sy) in enumerate(src):
                if i >= len(row):
                    continue
                weight = row[i]
                color = config.COLOR_EDGE_POS if weight >= 0 else config.COLOR_EDGE_NEG
                pygame.draw.line(self.screen, color, (sx, sy), (dx, dy), max(1, min(4, int(abs(weight) * 1.5))))

    def _draw_fitness_graph(self, sim, x: int, y: int, w: int, h: int) -> None:
        self.screen.blit(self.font_small.render("Beste Fitness je Generation", True, config.COLOR_TEXT_DIM), (x, y))
        gy, gh = y + 22, h - 22
        pygame.draw.rect(self.screen, (10, 12, 24), (x, gy, w, gh))
        pygame.draw.rect(self.screen, config.COLOR_NODE, (x, gy, w, gh), 1)

        history = sim.population.fitness_history
        if len(history) < 2:
            return
        peak = max(history) or 1.0
        n = len(history)
        points = [
            (x + int(w * (i / (n - 1))), gy + gh - int(gh * (v / peak)))
            for i, v in enumerate(history)
        ]
        pygame.draw.lines(self.screen, config.COLOR_ACCENT_2, False, points, 2)
