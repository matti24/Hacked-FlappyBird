"""Darstellung: cleaner, moderner Look mit performantem Rendering (Desktop & WASM).

Alle teuren Flächen (Himmel-Verlauf, Röhren-Textur, Vogel-Sprites) werden einmal
vorberechnet und pro Frame nur noch geblittet – das hält die FPS auch im Browser hoch.
"""

from __future__ import annotations

import math
import random
import sys

import pygame

from . import config


def _make_font(size: int, bold: bool = False) -> "pygame.font.Font":
    # Im Browser (pygbag/WASM) gibt es keine Systemfonts -> eingebaute Font.
    if sys.platform == "emscripten":
        return pygame.font.Font(None, size + 4)
    for name in ("Segoe UI", "segoeui", "Arial", "Helvetica"):
        try:
            font = pygame.font.SysFont(name, size, bold=bold)
            if font:
                return font
        except Exception:
            continue
    return pygame.font.Font(None, size + 4)


def _lerp(a, b, t: float):
    return (int(a[0] + (b[0] - a[0]) * t),
            int(a[1] + (b[1] - a[1]) * t),
            int(a[2] + (b[2] - a[2]) * t))


class Renderer:
    PAD = 20

    def __init__(self) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode((config.WIDTH, config.HEIGHT))
        pygame.display.set_caption("NeuroFlap – KI lernt fliegen")
        self.clock = pygame.time.Clock()

        self.font = _make_font(16)
        self.font_small = _make_font(13)
        self.font_big = _make_font(24, bold=True)
        self.font_stat = _make_font(30, bold=True)
        self.font_huge = _make_font(48, bold=True)
        self.font_label = _make_font(12)

        # Vorberechnete Flächen (einmalig).
        self._sky = self._make_sky()
        self._pipe_tex = self._make_pipe_texture()
        self._swarm_dot = self._make_swarm_dot()
        self._bird_best = self._make_bird_sprite(config.COLOR_BIRD_BEST, config.BIRD_RADIUS + 1)
        self._bird_player = self._make_bird_sprite(config.COLOR_PLAYER, config.BIRD_RADIUS + 1)
        self._trail_dots = self._make_trail_dots()

        rng = random.Random(7)
        self.stars = [
            (rng.randint(0, config.GAME_WIDTH), rng.randint(0, int(config.HEIGHT * 0.72)),
             rng.choice((1, 1, 1, 2)), rng.uniform(0, math.tau))
            for _ in range(config.STAR_COUNT)
        ]

        px = config.GAME_WIDTH + self.PAD
        pw = config.PANEL_WIDTH - 2 * self.PAD
        self.mode_rect = pygame.Rect(px, 92, pw, 36)
        self.toggle_rect = pygame.Rect(px, 140, pw, 42)
        self._trail: list[tuple[float, float]] = []

    # ------------------------------------------------------------------
    # Vorberechnete Flächen
    # ------------------------------------------------------------------
    def _make_sky(self) -> pygame.Surface:
        surf = pygame.Surface((config.GAME_WIDTH, config.HEIGHT))
        top, mid, bot = config.COLOR_SKY_TOP, config.COLOR_SKY_MID, config.COLOR_SKY_BOTTOM
        h = config.HEIGHT
        for y in range(h):
            f = y / h
            color = _lerp(top, mid, f / 0.55) if f < 0.55 else _lerp(mid, bot, (f - 0.55) / 0.45)
            pygame.draw.line(surf, color, (0, y), (config.GAME_WIDTH, y))
        return surf

    def _make_pipe_texture(self) -> pygame.Surface:
        # Volle-Höhe-Röhre mit horizontalem Verlauf; beim Zeichnen wird nur der
        # benötigte Ausschnitt geblittet (kein per-Frame-Gradient mehr).
        w, h = config.PIPE_WIDTH, config.HEIGHT
        tex = pygame.Surface((w, h))
        dark, light = config.COLOR_PIPE_DARK, config.COLOR_PIPE_LIGHT
        for col in range(w):
            f = 1 - abs(col - w / 2) / (w / 2)
            pygame.draw.line(tex, _lerp(dark, light, f ** 0.65), (col, 0), (col, h))
        return tex

    def _make_swarm_dot(self) -> pygame.Surface:
        r = config.BIRD_RADIUS
        size = r * 2 + 2
        s = pygame.Surface((size, size), pygame.SRCALPHA)
        c = size // 2
        pygame.draw.circle(s, (*config.COLOR_BIRD, 140), (c, c), r)
        pygame.draw.circle(s, (*config.COLOR_BIRD, 235), (c, c), r, 1)
        return s

    def _make_bird_sprite(self, color, radius: int) -> pygame.Surface:
        size = radius * 2 + 14
        s = pygame.Surface((size, size), pygame.SRCALPHA)
        c = size // 2
        pygame.draw.circle(s, color, (c, c), radius)
        pygame.draw.circle(s, (245, 250, 255), (c, c), radius, 2)
        eye = max(2, radius // 3)
        pygame.draw.circle(s, (255, 255, 255), (c + radius // 2, c - radius // 3), eye)
        pygame.draw.circle(s, (18, 22, 38), (c + radius // 2 + 1, c - radius // 3), max(1, eye // 2))
        pygame.draw.polygon(s, config.COLOR_AMBER, [
            (c + radius + 1, c - 1), (c + radius + 8, c - 3),
            (c + radius + 8, c + 4), (c + radius + 1, c + 3)])
        return s

    def _make_trail_dots(self) -> list[pygame.Surface]:
        dots = []
        n = 10
        for i in range(n):
            r = max(1, int(config.BIRD_RADIUS * 0.55 * (i / n)))
            a = int(70 * (i / n))
            surf = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*config.COLOR_BIRD_BEST, a), (r, r), r)
            dots.append(surf)
        return dots

    # ------------------------------------------------------------------
    # Haupt-Render
    # ------------------------------------------------------------------
    def render(self, sim, speed: int, active: bool = True) -> None:
        t = pygame.time.get_ticks() / 1000.0
        self._draw_world(t)
        self._draw_pipes(sim)
        self._draw_birds(sim)
        if sim.mode == "human" and sim.human_dead:
            self._draw_game_over(sim)
        self._draw_panel(sim, speed, active)
        self._draw_fps()
        pygame.display.flip()

    def _draw_world(self, t: float) -> None:
        self.screen.blit(self._sky, (0, 0))
        for (sx, sy, size, phase) in self.stars:
            tw = 0.55 + 0.45 * math.sin(t * 1.6 + phase)
            shade = int(80 + 130 * tw)
            self.screen.fill((shade, shade, min(255, shade + 45)), (sx, sy, size, size))
        gy = config.HEIGHT - 34
        self.screen.fill(config.COLOR_GROUND, (0, gy, config.GAME_WIDTH, 34))
        pygame.draw.line(self.screen, config.COLOR_GROUND_EDGE, (0, gy), (config.GAME_WIDTH, gy), 2)

    def _draw_fps(self) -> None:
        fps = self.clock.get_fps()
        txt = self.font_label.render(f"{fps:.0f} FPS", True, config.COLOR_TEXT_DIM)
        self.screen.blit(txt, (config.GAME_WIDTH - txt.get_width() - 12, 10))

    def _draw_pipes(self, sim) -> None:
        tex = self._pipe_tex
        w = config.PIPE_WIDTH
        cap = config.COLOR_PIPE_CAP
        edge = config.COLOR_PIPE_DARK
        H = config.HEIGHT
        for pipe in sim.pipes:
            x = int(pipe.x)
            top_h = int(pipe.gap_top)
            bot_y = int(pipe.gap_bottom)
            if top_h > 0:
                self.screen.blit(tex, (x, 0), (0, 0, w, top_h))
            bot_h = H - bot_y
            if bot_h > 0:
                self.screen.blit(tex, (x, bot_y), (0, 0, w, bot_h))
            pygame.draw.rect(self.screen, cap, (x - 5, top_h - 15, w + 10, 15), border_radius=6)
            pygame.draw.rect(self.screen, cap, (x - 5, bot_y, w + 10, 15), border_radius=6)
            pygame.draw.line(self.screen, edge, (x, 0), (x, top_h))
            pygame.draw.line(self.screen, edge, (x + w - 1, 0), (x + w - 1, top_h))
            pygame.draw.line(self.screen, edge, (x, bot_y), (x, H))
            pygame.draw.line(self.screen, edge, (x + w - 1, bot_y), (x + w - 1, H))

    # ------------------------------------------------------------------
    # Vögel
    # ------------------------------------------------------------------
    def _draw_birds(self, sim) -> None:
        if sim.mode == "human":
            if sim.player is not None:
                self._blit_bird(self._bird_player, sim.player.y, sim.player.velocity)
            return

        dot = self._swarm_dot
        off = dot.get_width() // 2
        bx = config.BIRD_X
        best = sim.population.best_alive()
        blit = self.screen.blit
        for bird in sim.population.birds:
            if bird.alive and bird is not best:
                blit(dot, (bx - off, int(bird.y) - off))
        if best is not None:
            self._draw_leader(best)

    def _draw_leader(self, bird) -> None:
        self._trail.append((float(config.BIRD_X), float(bird.y)))
        if len(self._trail) > len(self._trail_dots):
            self._trail.pop(0)
        for i, (tx, ty) in enumerate(self._trail[:-1]):
            surf = self._trail_dots[i]
            o = surf.get_width() // 2
            self.screen.blit(surf, (tx - o, ty - o))
        self._blit_bird(self._bird_best, bird.y, bird.velocity)

    def _blit_bird(self, sprite, y: float, velocity: float) -> None:
        angle = max(-30, min(60, -velocity * 4.0))
        rot = pygame.transform.rotate(sprite, angle)
        self.screen.blit(rot, rot.get_rect(center=(config.BIRD_X, int(y))))

    # ------------------------------------------------------------------
    # Panel
    # ------------------------------------------------------------------
    def _draw_panel(self, sim, speed: int, active: bool) -> None:
        px = config.GAME_WIDTH
        cx = px + self.PAD
        pw = config.PANEL_WIDTH - 2 * self.PAD
        self.screen.fill(config.COLOR_PANEL_BG, (px, 0, config.PANEL_WIDTH, config.HEIGHT))
        pygame.draw.line(self.screen, config.COLOR_CARD_BORDER, (px, 0), (px, config.HEIGHT), 1)

        self.screen.blit(self.font_big.render("NeuroFlap", True, config.COLOR_TEXT), (cx, 24))
        self.screen.blit(self.font_small.render("Neuroevolution · KI lernt fliegen", True, config.COLOR_TEXT_DIM), (cx, 56))

        self._draw_mode_switch(cx, pw, sim.mode)

        if sim.mode == "human":
            self._draw_human_panel(sim, cx, pw)
        else:
            self._draw_ai_panel(sim, speed, active, cx, pw)

        hint = ("Leertaste / Klick fliegen   ·   M: KI   ·   R: neu"
                if sim.mode == "human"
                else "M: selbst spielen   ·   Space: Pause   ·   1–5: Tempo   ·   R: Reset")
        self.screen.blit(self.font_label.render(hint, True, config.COLOR_TEXT_DIM), (cx, config.HEIGHT - 26))

    def _draw_mode_switch(self, cx: int, pw: int, mode: str) -> None:
        card = pygame.Rect(cx, 92, pw, 36)
        self.mode_rect = card
        pygame.draw.rect(self.screen, config.COLOR_CARD_BG, card, border_radius=10)
        half = card.width // 2
        ai_rect = pygame.Rect(card.x + 3, card.y + 3, half - 4, card.height - 6)
        hu_rect = pygame.Rect(card.x + half + 1, card.y + 3, half - 4, card.height - 6)
        active_rect = ai_rect if mode == "ai" else hu_rect
        pygame.draw.rect(self.screen, config.COLOR_MODE_ACTIVE, active_rect, border_radius=8)
        ai_col = (10, 18, 30) if mode == "ai" else config.COLOR_TEXT_DIM
        hu_col = (10, 18, 30) if mode == "human" else config.COLOR_TEXT_DIM
        a = self.font_small.render("KI-Training", True, ai_col)
        h = self.font_small.render("Selbst spielen", True, hu_col)
        self.screen.blit(a, a.get_rect(center=ai_rect.center))
        self.screen.blit(h, h.get_rect(center=hu_rect.center))

    def _draw_ai_panel(self, sim, speed: int, active: bool, cx: int, pw: int) -> None:
        pop = sim.population
        self._draw_toggle(cx, 140, pw, active)

        y = 196
        gap = 12
        cw = (pw - gap) // 2
        self._stat_card(cx, y, cw, "GENERATION", str(pop.generation), config.COLOR_ACCENT)
        self._stat_card(cx + cw + gap, y, cw, "BESTER SCORE", str(pop.best_score_ever), config.COLOR_AMBER)
        y += 86

        rows = [
            ("Vögel am Leben", f"{len(pop.alive_birds())} / {config.POPULATION_SIZE}"),
            ("Score aktuell", f"{sim.current_score()}"),
            ("Tempo", f"{sim.difficulty_speed(sim.current_score()):.1f}"),
            ("Simulationstempo", f"{speed}×"),
        ]
        for label, value in rows:
            self.screen.blit(self.font_small.render(label, True, config.COLOR_TEXT_DIM), (cx, y))
            val = self.font.render(value, True, config.COLOR_TEXT)
            self.screen.blit(val, (cx + pw - val.get_width(), y - 1))
            y += 26

        y += 2
        frac = len(pop.alive_birds()) / config.POPULATION_SIZE
        self._bar(cx, y, pw, frac, config.COLOR_ACCENT_2)
        y += 22

        net_h = 150
        self._draw_network(sim, cx, y, pw, net_h)
        y += net_h + 14
        self._draw_fitness_graph(sim, cx, y, pw, config.HEIGHT - y - 42)

    def _draw_human_panel(self, sim, cx: int, pw: int) -> None:
        y = 150
        card = pygame.Rect(cx, y, pw, 96)
        pygame.draw.rect(self.screen, config.COLOR_CARD_BG, card, border_radius=12)
        self.screen.blit(self.font_label.render("DEIN SCORE", True, config.COLOR_TEXT_DIM), (cx + 14, y + 12))
        self.screen.blit(self.font_huge.render(str(sim.human_score), True, config.COLOR_PLAYER), (cx + 12, y + 32))
        y += 116

        rows = [
            ("Dein Bestwert", f"{sim.human_best}"),
            ("KI-Bestwert", f"{sim.population.best_score_ever}"),
            ("Tempo", f"{sim.difficulty_speed(sim.human_score):.1f}"),
            ("Lücke", f"{int(sim.difficulty_gap(sim.human_score))} px"),
        ]
        for label, value in rows:
            self.screen.blit(self.font_small.render(label, True, config.COLOR_TEXT_DIM), (cx, y))
            val = self.font.render(value, True, config.COLOR_TEXT)
            self.screen.blit(val, (cx + pw - val.get_width(), y - 1))
            y += 30

        y += 16
        for line in ("Schaffst du mehr", "als die KI?"):
            self.screen.blit(self.font.render(line, True, config.COLOR_TEXT_DIM), (cx, y))
            y += 26

    # ------------------------------------------------------------------
    # Panel-Bausteine
    # ------------------------------------------------------------------
    def _stat_card(self, x: int, y: int, w: int, label: str, value: str, accent) -> None:
        pygame.draw.rect(self.screen, config.COLOR_CARD_BG, (x, y, w, 72), border_radius=10)
        self.screen.blit(self.font_label.render(label, True, config.COLOR_TEXT_DIM), (x + 12, y + 11))
        self.screen.blit(self.font_stat.render(value, True, accent), (x + 12, y + 30))

    def _bar(self, x: int, y: int, w: int, frac: float, color) -> None:
        pygame.draw.rect(self.screen, config.COLOR_CARD_BG, (x, y, w, 8), border_radius=4)
        fw = max(0, min(w, int(w * frac)))
        if fw > 0:
            pygame.draw.rect(self.screen, color, (x, y, fw, 8), border_radius=4)

    def _draw_toggle(self, cx: int, y: int, pw: int, active: bool) -> None:
        card = pygame.Rect(cx, y, pw, 42)
        self.toggle_rect = card
        pygame.draw.rect(self.screen, config.COLOR_CARD_BG, card, border_radius=10)
        pygame.draw.rect(self.screen, config.COLOR_ACCENT_2 if active else config.COLOR_CARD_BORDER, card, 1, border_radius=10)
        label = "Simulation läuft" if active else "Pausiert"
        self.screen.blit(self.font_small.render(label, True, config.COLOR_TEXT), (card.x + 14, card.y + 13))
        sw_w, sw_h = 44, 22
        sx = card.right - sw_w - 12
        sy = card.y + (card.height - sw_h) // 2
        pygame.draw.rect(self.screen, config.COLOR_TOGGLE_ON if active else config.COLOR_TOGGLE_OFF, (sx, sy, sw_w, sw_h), border_radius=11)
        knob_x = sx + sw_w - sw_h // 2 if active else sx + sw_h // 2
        pygame.draw.circle(self.screen, config.COLOR_TOGGLE_KNOB, (knob_x, sy + sw_h // 2), sw_h // 2 - 3)

    def _draw_network(self, sim, x: int, y: int, w: int, h: int) -> None:
        pygame.draw.rect(self.screen, config.COLOR_CARD_BG, (x, y, w, h), border_radius=10)
        self.screen.blit(self.font_label.render("GEHIRN DES ANFÜHRERS", True, config.COLOR_TEXT_DIM), (x + 12, y + 10))
        best = sim.population.best_alive()
        brain = best.brain if best is not None else None
        layers = (config.INPUT_SIZE, config.HIDDEN_SIZE, config.OUTPUT_SIZE)
        acts = [brain.last_input, brain.last_hidden, brain.last_output] if brain else None

        top = y + 34
        area_h = h - 46
        inner_x = x + 24
        inner_w = w - 48
        positions: list[list[tuple[int, int]]] = []
        for li, count in enumerate(layers):
            lx = inner_x + int(inner_w * (li / (len(layers) - 1)))
            positions.append([(lx, top + int(area_h * ((n + 0.5) / count))) for n in range(count)])

        if brain is not None:
            self._edges(positions[0], positions[1], brain.w1)
            self._edges(positions[1], positions[2], brain.w2)
        for li, col in enumerate(positions):
            for n, (nx, ny) in enumerate(col):
                act = abs(acts[li][n]) if acts and n < len(acts[li]) else 0.0
                color = _lerp(config.COLOR_NODE, config.COLOR_NODE_ON, min(1.0, act))
                pygame.draw.circle(self.screen, color, (nx, ny), 7)
                pygame.draw.circle(self.screen, config.COLOR_CARD_BORDER, (nx, ny), 7, 1)

    def _edges(self, src, dst, weights) -> None:
        for j, (dx, dy) in enumerate(dst):
            row = weights[j] if j < len(weights) else []
            for i, (sx, sy) in enumerate(src):
                if i < len(row):
                    weight = row[i]
                    color = config.COLOR_EDGE_POS if weight >= 0 else config.COLOR_EDGE_NEG
                    pygame.draw.line(self.screen, color, (sx, sy), (dx, dy), max(1, min(3, int(abs(weight) * 1.4))))

    def _draw_fitness_graph(self, sim, x: int, y: int, w: int, h: int) -> None:
        if h < 46:
            return
        pygame.draw.rect(self.screen, config.COLOR_CARD_BG, (x, y, w, h), border_radius=10)
        self.screen.blit(self.font_label.render("FITNESS JE GENERATION", True, config.COLOR_TEXT_DIM), (x + 12, y + 10))
        gx, gy = x + 12, y + 32
        gw, gh = w - 24, h - 44
        history = sim.population.fitness_history
        if len(history) < 2:
            return
        peak = max(history) or 1.0
        n = len(history)
        points = [(gx + int(gw * (i / (n - 1))), gy + gh - int(gh * (v / peak))) for i, v in enumerate(history)]
        fill = pygame.Surface((w, h), pygame.SRCALPHA)
        poly = [(px_ - x, py_ - y) for px_, py_ in points] + [(points[-1][0] - x, gy + gh - y), (points[0][0] - x, gy + gh - y)]
        pygame.draw.polygon(fill, (*config.COLOR_ACCENT, 45), poly)
        self.screen.blit(fill, (x, y))
        pygame.draw.lines(self.screen, config.COLOR_ACCENT, False, points, 2)

    def _draw_game_over(self, sim) -> None:
        overlay = pygame.Surface((config.GAME_WIDTH, config.HEIGHT), pygame.SRCALPHA)
        overlay.fill((8, 12, 24, 175))
        self.screen.blit(overlay, (0, 0))
        cx, cy = config.GAME_WIDTH // 2, config.HEIGHT // 2
        title = self.font_huge.render("Game Over", True, config.COLOR_TEXT)
        self.screen.blit(title, title.get_rect(center=(cx, cy - 54)))
        score = self.font_big.render(f"Dein Score: {sim.human_score}", True, config.COLOR_PLAYER)
        self.screen.blit(score, score.get_rect(center=(cx, cy)))
        cmp = self.font.render(f"KI-Bestwert: {sim.population.best_score_ever}", True, config.COLOR_AMBER)
        self.screen.blit(cmp, cmp.get_rect(center=(cx, cy + 38)))
        again = self.font_small.render("Leertaste oder Klick für neuen Versuch", True, config.COLOR_TEXT_DIM)
        self.screen.blit(again, again.get_rect(center=(cx, cy + 76)))
