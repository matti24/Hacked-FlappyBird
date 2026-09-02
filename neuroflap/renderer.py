"""Darstellung: Landschafts-Hintergrund, KI-Schwarm, Mensch-Modus und Netz-Visualisierung."""

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
        self.font_huge = pygame.font.SysFont("consolas", 54, bold=True)
        self.font_label = pygame.font.SysFont("consolas", 13)

        self._bg = self._make_gradient()

        rng = random.Random(42)
        self.stars = [
            (rng.uniform(0, config.GAME_WIDTH), rng.uniform(0, config.HEIGHT * 0.6),
             rng.uniform(0.6, 2.1), rng.uniform(0, math.tau), rng.uniform(4, 16))
            for _ in range(config.STAR_COUNT)
        ]
        self.nebulae = [
            (self._radial_glow(230, config.COLOR_NEBULA_A, 42), 150, 170, 12.0),
            (self._radial_glow(200, config.COLOR_NEBULA_B, 36), 560, 300, 16.0),
        ]
        # Parallax-Bergketten (Surface, Drift-Tempo) von fern nach nah.
        self.mountains = [
            (self._make_mountain_layer(config.COLOR_MOUNTAIN_FAR, config.HEIGHT * 0.62, 110, 7, 1), 8.0),
            (self._make_mountain_layer(config.COLOR_MOUNTAIN_MID, config.HEIGHT * 0.74, 150, 9, 2), 15.0),
            (self._make_mountain_layer(config.COLOR_MOUNTAIN_NEAR, config.HEIGHT * 0.88, 190, 11, 3), 26.0),
        ]
        self.moon_pos = (int(config.GAME_WIDTH * 0.76), int(config.HEIGHT * 0.22))
        self.moon_r = 46
        self._moon_glow = self._radial_glow(120, config.COLOR_MOON_GLOW, 90)

        self._bird_glow = self._radial_glow(int(config.BIRD_RADIUS * 2.3), config.COLOR_BIRD_GLOW, 60)
        self._leader_aura = self._radial_glow(config.BIRD_RADIUS * 4, config.COLOR_LEADER_AURA, 150)
        self._player_aura = self._radial_glow(config.BIRD_RADIUS * 4, config.COLOR_PLAYER, 120)

        self.mode_rect = pygame.Rect(config.GAME_WIDTH + 18, 78, config.PANEL_WIDTH - 36, 34)
        self.toggle_rect = pygame.Rect(config.GAME_WIDTH + 18, 120, config.PANEL_WIDTH - 36, 38)
        self._trail: list[tuple[float, float]] = []

    # ------------------------------------------------------------------
    # Hilfssurfaces
    # ------------------------------------------------------------------
    def _make_gradient(self) -> pygame.Surface:
        surf = pygame.Surface((config.GAME_WIDTH, config.HEIGHT))
        top, bottom = config.COLOR_BG_TOP, config.COLOR_BG_BOTTOM
        for y in range(config.HEIGHT):
            f = y / config.HEIGHT
            color = tuple(int(top[i] + (bottom[i] - top[i]) * f) for i in range(3))
            pygame.draw.line(surf, color, (0, y), (config.GAME_WIDTH, y))
        return surf

    def _radial_glow(self, radius: int, color: tuple[int, int, int], max_alpha: int) -> pygame.Surface:
        surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        for r in range(radius, 0, -1):
            alpha = int(max_alpha * (1 - r / radius) ** 2)
            if alpha > 0:
                pygame.draw.circle(surf, (*color, alpha), (radius, radius), r)
        return surf

    def _make_mountain_layer(self, color, base_y, amplitude, segments, seed) -> pygame.Surface:
        rng = random.Random(seed)
        w = config.GAME_WIDTH
        surf = pygame.Surface((w, config.HEIGHT), pygame.SRCALPHA)
        heights = [rng.uniform(0.25, 1.0) * amplitude for _ in range(segments)]
        heights.append(heights[0])  # nahtloser Übergang beim Scrollen
        points = [(0, config.HEIGHT)]
        for i, h in enumerate(heights):
            points.append((w * i / (len(heights) - 1), base_y - h))
        points.append((w, config.HEIGHT))
        pygame.draw.polygon(surf, color, points)
        return surf

    # ------------------------------------------------------------------
    # Haupt-Render
    # ------------------------------------------------------------------
    def render(self, sim, speed: int, active: bool = True) -> None:
        t = pygame.time.get_ticks() / 1000.0
        self._draw_background(t)
        self._draw_pipes(sim, t)
        self._draw_birds(sim, t)
        if sim.mode == "human" and sim.human_dead:
            self._draw_human_overlay(sim)
        self._draw_panel(sim, speed, active, t)
        pygame.display.flip()

    def _draw_background(self, t: float) -> None:
        self.screen.blit(self._bg, (0, 0))

        for (sx, sy, size, phase, drift) in self.stars:
            x = (sx - t * drift) % config.GAME_WIDTH
            twinkle = 0.5 + 0.5 * math.sin(t * 2.2 + phase)
            shade = int(120 + 135 * twinkle)
            pygame.draw.circle(self.screen, (shade, shade, min(255, shade + 40)), (int(x), int(sy)), max(1, int(size)))

        for surf, bx, by, drift in self.nebulae:
            dx = (bx - t * drift) % (config.GAME_WIDTH + 460) - 230
            self.screen.blit(surf, (dx, by - surf.get_height() / 2), special_flags=pygame.BLEND_ADD)

        # Mond mit weichem Schein.
        mx, my = self.moon_pos
        self.screen.blit(self._moon_glow, (mx - 120, my - 120), special_flags=pygame.BLEND_ADD)
        pygame.draw.circle(self.screen, config.COLOR_MOON, (mx, my), self.moon_r)
        pygame.draw.circle(self.screen, (208, 206, 188), (mx - 14, my - 10), 8)
        pygame.draw.circle(self.screen, (208, 206, 188), (mx + 12, my + 8), 6)
        pygame.draw.circle(self.screen, (208, 206, 188), (mx + 4, my - 16), 4)

        # Parallax-Bergketten.
        for surf, drift in self.mountains:
            offset = int(t * drift) % config.GAME_WIDTH
            self.screen.blit(surf, (-offset, 0))
            self.screen.blit(surf, (config.GAME_WIDTH - offset, 0))

    def _draw_pipes(self, sim, t: float) -> None:
        pulse = 0.5 + 0.5 * math.sin(t * 4.0)
        for pipe in sim.pipes:
            x = int(pipe.x)
            w = config.PIPE_WIDTH
            top_h = int(pipe.gap_top)
            bot_y = int(pipe.gap_bottom)

            glow = pygame.Surface((w + 24, config.HEIGHT), pygame.SRCALPHA)
            glow.fill((*config.COLOR_PIPE_GLOW, 24))
            self.screen.blit(glow, (x - 12, 0), special_flags=pygame.BLEND_ADD)

            self._draw_pipe_body(x, 0, w, top_h)
            self._draw_pipe_body(x, bot_y, w, config.HEIGHT - bot_y)

            cap_color = tuple(int(config.COLOR_PIPE_CAP[i] * (0.7 + 0.3 * pulse)) for i in range(3))
            pygame.draw.rect(self.screen, cap_color, (x - 4, top_h - 14, w + 8, 14), border_radius=5)
            pygame.draw.rect(self.screen, cap_color, (x - 4, bot_y, w + 8, 14), border_radius=5)

    def _draw_pipe_body(self, x: int, y: int, w: int, h: int) -> None:
        if h <= 0:
            return
        body = pygame.Surface((w, h))
        core, glow = config.COLOR_PIPE_CORE, config.COLOR_PIPE_GLOW
        for col in range(w):
            f = 1 - abs(col - w / 2) / (w / 2)
            shade = tuple(int(core[i] + (glow[i] - core[i]) * f * 0.55) for i in range(3))
            pygame.draw.line(body, shade, (col, 0), (col, h))
        self.screen.blit(body, (x, y))
        pygame.draw.rect(self.screen, config.COLOR_PIPE_CAP, (x, y, w, h), 2)

    # ------------------------------------------------------------------
    # Vögel
    # ------------------------------------------------------------------
    def _bird_sprite(self, color, velocity: float, t: float) -> pygame.Surface:
        size = config.BIRD_RADIUS * 4
        s = pygame.Surface((size, size), pygame.SRCALPHA)
        cx = cy = size // 2
        r = config.BIRD_RADIUS + 1
        pygame.draw.circle(s, color, (cx, cy), r)
        pygame.draw.circle(s, (255, 255, 255), (cx, cy), r, 2)
        wing = math.sin(t * 16) * 4
        pygame.draw.ellipse(s, config.COLOR_BIRD_WING, (cx - 11, cy - 2 + wing, 13, 9))
        pygame.draw.circle(s, (255, 255, 255), (cx + 5, cy - 4), 3)
        pygame.draw.circle(s, (18, 18, 30), (cx + 6, cy - 4), 1)
        pygame.draw.polygon(s, (250, 175, 60), [(cx + r, cy), (cx + r + 8, cy - 2), (cx + r + 8, cy + 3)])
        angle = max(-32, min(65, -velocity * 4.5))
        return pygame.transform.rotate(s, angle)

    def _draw_birds(self, sim, t: float) -> None:
        if sim.mode == "human":
            if sim.player is not None:
                pos = (config.BIRD_X, int(sim.player.y))
                ar = self._player_aura.get_width() / 2
                self.screen.blit(self._player_aura, (pos[0] - ar, pos[1] - ar), special_flags=pygame.BLEND_ADD)
                sprite = self._bird_sprite(config.COLOR_PLAYER, sim.player.velocity, t)
                self.screen.blit(sprite, sprite.get_rect(center=pos))
            return

        best = sim.population.best_alive()
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
        ar = self._leader_aura.get_width() / 2
        self.screen.blit(self._leader_aura, (pos[0] - ar, pos[1] - ar), special_flags=pygame.BLEND_ADD)

        self._trail.append((float(pos[0]), float(pos[1])))
        if len(self._trail) > 14:
            self._trail.pop(0)
        for i, (tx, ty) in enumerate(self._trail[:-1]):
            alpha = int(120 * (i / len(self._trail)))
            r = max(1, int(config.BIRD_RADIUS * 0.5 * (i / len(self._trail))))
            dot = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
            pygame.draw.circle(dot, (*config.COLOR_BIRD_BEST, alpha), (r, r), r)
            self.screen.blit(dot, (tx - r, ty - r), special_flags=pygame.BLEND_ADD)

        sprite = self._bird_sprite(config.COLOR_BIRD_BEST, bird.velocity, t)
        self.screen.blit(sprite, sprite.get_rect(center=pos))

    def _draw_human_overlay(self, sim) -> None:
        overlay = pygame.Surface((config.GAME_WIDTH, config.HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))
        cx, cy = config.GAME_WIDTH // 2, config.HEIGHT // 2
        title = self.font_huge.render("GAME OVER", True, (235, 110, 110))
        self.screen.blit(title, title.get_rect(center=(cx, cy - 50)))
        score = self.font_big.render(f"Dein Score: {sim.human_score}", True, config.COLOR_TEXT)
        self.screen.blit(score, score.get_rect(center=(cx, cy + 6)))
        cmp = self.font.render(f"Die KI schafft bis zu {sim.population.best_score_ever}", True, config.COLOR_BIRD_BEST)
        self.screen.blit(cmp, cmp.get_rect(center=(cx, cy + 42)))
        again = self.font.render("Leertaste / Klick für neuen Versuch", True, config.COLOR_TEXT_DIM)
        self.screen.blit(again, again.get_rect(center=(cx, cy + 78)))

    # ------------------------------------------------------------------
    # Panel
    # ------------------------------------------------------------------
    def _draw_panel(self, sim, speed: int, active: bool, t: float) -> None:
        px = config.GAME_WIDTH
        pygame.draw.rect(self.screen, config.COLOR_PANEL_BG, (px, 0, config.PANEL_WIDTH, config.HEIGHT))
        pygame.draw.line(self.screen, config.COLOR_ACCENT, (px, 0), (px, config.HEIGHT), 2)
        cx = px + 20

        self.screen.blit(self.font_big.render("NeuroFlap", True, config.COLOR_TEXT), (cx, 14))
        self.screen.blit(self.font_small.render("KI lernt per Neuroevolution", True, config.COLOR_TEXT_DIM), (cx, 48))

        self._draw_mode_switch(px, sim.mode)

        if sim.mode == "human":
            self._draw_human_panel(sim, px, cx)
        else:
            self._draw_ai_panel(sim, speed, active, px, cx)

        hint = ("Fliegen: Leertaste/Klick   M KI-Modus   R Neu   Esc"
                if sim.mode == "human"
                else "M Selbst spielen   Klick/Space An/Aus   1-5 Tempo   R Reset")
        self.screen.blit(self.font_label.render(hint, True, config.COLOR_TEXT_DIM), (cx, config.HEIGHT - 24))

    def _draw_mode_switch(self, px: int, mode: str) -> None:
        card = pygame.Rect(px + 18, 78, config.PANEL_WIDTH - 36, 34)
        self.mode_rect = card
        pygame.draw.rect(self.screen, config.COLOR_CARD_BG, card, border_radius=9)
        half = card.width // 2
        ai_rect = pygame.Rect(card.x + 2, card.y + 2, half - 3, card.height - 4)
        hu_rect = pygame.Rect(card.x + half + 1, card.y + 2, half - 3, card.height - 4)
        pygame.draw.rect(self.screen, config.COLOR_MODE_ACTIVE if mode == "ai" else config.COLOR_MODE_INACTIVE, ai_rect, border_radius=7)
        pygame.draw.rect(self.screen, config.COLOR_MODE_ACTIVE if mode == "human" else config.COLOR_MODE_INACTIVE, hu_rect, border_radius=7)
        a = self.font_small.render("KI-Training", True, config.COLOR_TEXT)
        h = self.font_small.render("Selbst spielen", True, config.COLOR_TEXT)
        self.screen.blit(a, a.get_rect(center=ai_rect.center))
        self.screen.blit(h, h.get_rect(center=hu_rect.center))

    def _draw_ai_panel(self, sim, speed: int, active: bool, px: int, cx: int) -> None:
        self._draw_toggle(px, 120, active)
        pop = sim.population
        rows = [
            ("Generation", f"{pop.generation}", config.COLOR_ACCENT_2),
            ("Vögel am Leben", f"{len(pop.alive_birds())} / {config.POPULATION_SIZE}", config.COLOR_TEXT),
            ("Score aktuell", f"{sim.current_score()}", config.COLOR_TEXT),
            ("Bester Score", f"{pop.best_score_ever}", config.COLOR_BIRD_BEST),
            ("Tempo", f"{config.PIPE_SPEED + min(sim.current_score() * config.DIFF_SPEED_PER_SCORE, config.PIPE_SPEED_MAX_BONUS):.1f}", config.COLOR_ACCENT_2),
            ("Simulationstempo", f"{speed}x", config.COLOR_ACCENT),
        ]
        y = 172
        for label, value, color in rows:
            self.screen.blit(self.font_small.render(label, True, config.COLOR_TEXT_DIM), (cx, y))
            val = self.font.render(value, True, color)
            self.screen.blit(val, (px + config.PANEL_WIDTH - 20 - val.get_width(), y - 2))
            y += 24

        self._draw_network(sim, px + 16, y + 4, config.PANEL_WIDTH - 32, 176)
        self._draw_fitness_graph(sim, px + 16, y + 210, config.PANEL_WIDTH - 32, 104)

    def _draw_human_panel(self, sim, px: int, cx: int) -> None:
        y = 132
        self.screen.blit(self.font_small.render("Dein Score", True, config.COLOR_TEXT_DIM), (cx, y))
        big = self.font_huge.render(str(sim.human_score), True, config.COLOR_PLAYER)
        self.screen.blit(big, (cx, y + 18))

        y += 96
        rows = [
            ("Dein Bestwert", f"{sim.human_best}", config.COLOR_PLAYER),
            ("KI-Bestwert", f"{sim.population.best_score_ever}", config.COLOR_BIRD_BEST),
            ("Aktuelles Tempo", f"{sim.difficulty_speed(sim.human_score):.1f}", config.COLOR_ACCENT_2),
            ("Lücke", f"{int(sim.difficulty_gap(sim.human_score))} px", config.COLOR_TEXT),
        ]
        for label, value, color in rows:
            self.screen.blit(self.font_small.render(label, True, config.COLOR_TEXT_DIM), (cx, y))
            val = self.font.render(value, True, color)
            self.screen.blit(val, (px + config.PANEL_WIDTH - 20 - val.get_width(), y - 2))
            y += 28

        y += 12
        for line in ["So schwer ist es!", "Schaffst du mehr", "als die KI?"]:
            self.screen.blit(self.font_small.render(line, True, config.COLOR_TEXT_DIM), (cx, y))
            y += 22

    def _draw_toggle(self, px: int, y: int, active: bool) -> None:
        card = pygame.Rect(px + 18, y, config.PANEL_WIDTH - 36, 38)
        self.toggle_rect = card
        pygame.draw.rect(self.screen, config.COLOR_CARD_BG, card, border_radius=10)
        pygame.draw.rect(self.screen, config.COLOR_ACCENT if active else config.COLOR_TOGGLE_OFF, card, 1, border_radius=10)
        label = "Simulation läuft" if active else "Simulation pausiert"
        self.screen.blit(self.font_small.render(label, True, config.COLOR_TEXT), (card.x + 12, card.y + 11))
        sw_w, sw_h = 46, 22
        sx = card.right - sw_w - 12
        sy = card.y + (card.height - sw_h) // 2
        pygame.draw.rect(self.screen, config.COLOR_TOGGLE_ON if active else config.COLOR_TOGGLE_OFF, (sx, sy, sw_w, sw_h), border_radius=11)
        knob_x = sx + sw_w - sw_h // 2 - 2 if active else sx + sw_h // 2 + 2
        pygame.draw.circle(self.screen, config.COLOR_TOGGLE_KNOB, (knob_x, sy + sw_h // 2), sw_h // 2 - 3)

    def _draw_network(self, sim, x: int, y: int, w: int, h: int) -> None:
        self.screen.blit(self.font_small.render("Gehirn des Anführers", True, config.COLOR_TEXT_DIM), (x, y))
        top = y + 22
        area_h = h - 22
        best = sim.population.best_alive()
        brain = best.brain if best is not None else None
        layers = [config.INPUT_SIZE, config.HIDDEN_SIZE, config.OUTPUT_SIZE]
        activations = [brain.last_input, brain.last_hidden, brain.last_output] if brain else None

        positions: list[list[tuple[int, int]]] = []
        for li, count in enumerate(layers):
            lx = min(max(x + int(w * (li / (len(layers) - 1))), x + 14), x + w - 14)
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
                if i < len(row):
                    color = config.COLOR_EDGE_POS if row[i] >= 0 else config.COLOR_EDGE_NEG
                    pygame.draw.line(self.screen, color, (sx, sy), (dx, dy), max(1, min(4, int(abs(row[i]) * 1.5))))

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
        points = [(x + int(w * (i / (n - 1))), gy + gh - int(gh * (v / peak))) for i, v in enumerate(history)]
        pygame.draw.lines(self.screen, config.COLOR_ACCENT_2, False, points, 2)
