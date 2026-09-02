"""Darstellung des Spiels mit pygame."""

from __future__ import annotations

import pygame

from . import config


class Renderer:
    def __init__(self) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
        pygame.display.set_caption("Dark Depths")
        self.clock = pygame.time.Clock()
        self.tile_font = pygame.font.SysFont("consolas", int(config.TILE_SIZE * 0.95), bold=True)
        self.ui_font = pygame.font.SysFont("consolas", 17)
        self.ui_font_bold = pygame.font.SysFont("consolas", 17, bold=True)
        self.big_font = pygame.font.SysFont("consolas", 46, bold=True)
        self._char_cache: dict[tuple[str, tuple[int, int, int]], pygame.Surface] = {}

    def _char_surface(self, char: str, color: tuple[int, int, int]) -> pygame.Surface:
        key = (char, color)
        surf = self._char_cache.get(key)
        if surf is None:
            surf = self.tile_font.render(char, True, color)
            self._char_cache[key] = surf
        return surf

    def _blit_char(self, char: str, color: tuple[int, int, int], tx: int, ty: int) -> None:
        surf = self._char_surface(char, color)
        ts = config.TILE_SIZE
        rect = surf.get_rect(center=(tx * ts + ts // 2, ty * ts + ts // 2))
        self.screen.blit(surf, rect)

    def render(self, game) -> None:
        self.screen.fill(config.COLOR_BG)
        self._draw_map(game)
        self._draw_entities(game)
        self._draw_panel(game)
        if game.game_over:
            self._draw_overlay(game)
        pygame.display.flip()

    def _draw_map(self, game) -> None:
        gm = game.game_map
        ts = config.TILE_SIZE
        for x in range(gm.width):
            column = gm.tiles[x]
            for y in range(gm.height):
                tile = column[y]
                visible = (x, y) in gm.visible
                if not visible and not tile.explored:
                    continue
                if tile.walkable:
                    color = config.COLOR_LIGHT_GROUND if visible else config.COLOR_DARK_GROUND
                else:
                    color = config.COLOR_LIGHT_WALL if visible else config.COLOR_DARK_WALL
                pygame.draw.rect(self.screen, color, (x * ts, y * ts, ts - 1, ts - 1))

        stairs = gm.stairs_down
        if stairs is not None:
            sx, sy = stairs
            if (sx, sy) in gm.visible or gm.tiles[sx][sy].explored:
                self._blit_char(">", config.COLOR_STAIRS, sx, sy)

    def _draw_entities(self, game) -> None:
        # Items zuerst, damit Wesen darüber liegen.
        ordered = sorted(game.entities, key=lambda e: getattr(e, "blocks_movement", True))
        for entity in ordered:
            if entity.pos in game.game_map.visible:
                self._blit_char(entity.char, entity.color, entity.x, entity.y)

    def _draw_panel(self, game) -> None:
        top = config.MAP_HEIGHT * config.TILE_SIZE
        pygame.draw.rect(
            self.screen, config.COLOR_PANEL_BG,
            (0, top, config.SCREEN_WIDTH, config.PANEL_HEIGHT),
        )
        pygame.draw.line(self.screen, config.COLOR_ACCENT, (0, top), (config.SCREEN_WIDTH, top), 2)

        player = game.player
        pad = 14

        # HP-Balken (oben links)
        bar_w, bar_h = 200, 22
        bx, by = pad, top + 12
        pygame.draw.rect(self.screen, config.COLOR_HP_BAR_BG, (bx, by, bar_w, bar_h), border_radius=4)
        ratio = max(0.0, player.hp / player.max_hp)
        pygame.draw.rect(self.screen, config.COLOR_HP_BAR, (bx, by, int(bar_w * ratio), bar_h), border_radius=4)
        self.screen.blit(
            self.ui_font_bold.render(f"HP {player.hp}/{player.max_hp}", True, config.COLOR_TEXT),
            (bx + 8, by + 2),
        )

        # Statuszeile (eigene Zeile unter der HP-Bar)
        stats = f"Ebene {game.dungeon_level}    Tränke {game.potions}    Angriff {player.power}    Verteidigung {player.defense}"
        self.screen.blit(self.ui_font.render(stats, True, config.COLOR_TEXT_DIM), (pad, by + bar_h + 12))

        # Nachrichten-Log (rechte Bildschirmhälfte)
        log_x = config.SCREEN_WIDTH // 2
        self.screen.blit(self.ui_font_bold.render("Ereignisse", True, config.COLOR_ACCENT), (log_x, top + 12))
        for i, (text, color) in enumerate(game.messages[-config.MESSAGE_LOG_LINES:]):
            self.screen.blit(self.ui_font.render(text, True, color), (log_x, top + 38 + i * 20))

        # Steuerung (unten über die volle Breite)
        hint = "Bewegen: WASD/Pfeile      Trank: Q      Abstieg: >      Neustart: R      Beenden: Esc"
        self.screen.blit(
            self.ui_font.render(hint, True, config.COLOR_TEXT_DIM),
            (pad, top + config.PANEL_HEIGHT - 26),
        )

    def _draw_overlay(self, game) -> None:
        overlay = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 170))
        self.screen.blit(overlay, (0, 0))

        if game.won:
            title, color = "SIEG!", config.COLOR_MSG_GOOD
            sub = f"Du hast die Tiefen bezwungen – Ebene {game.dungeon_level} erreicht."
        else:
            title, color = "DU BIST GEFALLEN", config.COLOR_MSG_BAD
            sub = f"Vorgedrungen bis Ebene {game.dungeon_level}."

        t_surf = self.big_font.render(title, True, color)
        s_surf = self.ui_font.render(sub, True, config.COLOR_TEXT)
        r_surf = self.ui_font.render("Drücke R für einen neuen Versuch oder Esc zum Beenden.", True, config.COLOR_TEXT_DIM)
        cx = config.SCREEN_WIDTH // 2
        cy = config.SCREEN_HEIGHT // 2
        self.screen.blit(t_surf, t_surf.get_rect(center=(cx, cy - 40)))
        self.screen.blit(s_surf, s_surf.get_rect(center=(cx, cy + 10)))
        self.screen.blit(r_surf, r_surf.get_rect(center=(cx, cy + 40)))
