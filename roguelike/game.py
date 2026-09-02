"""Spielzustand, Rundenlogik und Hauptschleife."""

from __future__ import annotations

import random

from . import config
from .combat import attack
from .entities import (
    Actor,
    Item,
    make_goblin,
    make_orc,
    make_player,
    make_potion,
    make_troll,
)
from .fov import compute_fov
from .procgen import generate_dungeon


class Game:
    """Kapselt den gesamten Spielzustand – bewusst frei von pygame (testbar)."""

    def __init__(self, seed: int | None = None) -> None:
        self.rng = random.Random(seed)
        self.dungeon_level = 0
        self.player = make_player(0, 0)
        self.potions = 0
        self.messages: list[tuple[str, tuple[int, int, int]]] = []
        self.entities: list[Actor | Item] = []
        self.game_over = False
        self.won = False
        self.game_map = None  # in _next_level gesetzt
        self._next_level()
        self.add_message("Du betrittst die Dunklen Tiefen …", config.COLOR_MSG_INFO)

    # ------------------------------------------------------------------
    # Level-Aufbau
    # ------------------------------------------------------------------
    def _next_level(self) -> None:
        self.dungeon_level += 1
        self.game_map, rooms = generate_dungeon(
            config.MAP_WIDTH,
            config.MAP_HEIGHT,
            max_rooms=config.MAX_ROOMS,
            room_min_size=config.ROOM_MIN_SIZE,
            room_max_size=config.ROOM_MAX_SIZE,
            rng=self.rng,
        )
        start = rooms[0].center if rooms else (config.MAP_WIDTH // 2, config.MAP_HEIGHT // 2)
        self.player.pos = start
        self.entities = [self.player]
        self._spawn_entities(rooms)
        self.update_fov()

    def _spawn_entities(self, rooms) -> None:
        for room in rooms[1:]:  # erster Raum bleibt frei (Spielerstart)
            tiles = room.inner_tiles()
            self.rng.shuffle(tiles)
            cursor = 0

            for _ in range(self.rng.randint(0, config.MAX_MONSTERS_PER_ROOM)):
                if cursor >= len(tiles):
                    break
                pos = tiles[cursor]
                cursor += 1
                if self.actor_at(pos) is None:
                    self.entities.append(self._random_monster(pos))

            for _ in range(self.rng.randint(0, config.MAX_ITEMS_PER_ROOM)):
                if cursor >= len(tiles):
                    break
                pos = tiles[cursor]
                cursor += 1
                self.entities.append(make_potion(*pos))

    def _random_monster(self, pos: tuple[int, int]) -> Actor:
        roll = self.rng.random()
        troll_chance = min(0.35, 0.03 * self.dungeon_level)
        orc_chance = min(0.5, 0.12 + 0.05 * self.dungeon_level)
        if roll < troll_chance:
            return make_troll(*pos)
        if roll < troll_chance + orc_chance:
            return make_orc(*pos)
        return make_goblin(*pos)

    # ------------------------------------------------------------------
    # Abfragen
    # ------------------------------------------------------------------
    def actor_at(self, pos: tuple[int, int]) -> Actor | None:
        for e in self.entities:
            if isinstance(e, Actor) and e.is_alive and e.pos == pos:
                return e
        return None

    def blocking_positions(self, exclude: Actor | None = None) -> set[tuple[int, int]]:
        result: set[tuple[int, int]] = set()
        for e in self.entities:
            if e is exclude or not e.blocks_movement:
                continue
            if isinstance(e, Actor) and not e.is_alive:
                continue
            result.add(e.pos)
        return result

    # ------------------------------------------------------------------
    # Sichtfeld
    # ------------------------------------------------------------------
    def update_fov(self) -> None:
        visible = compute_fov(self.game_map, self.player.pos, config.FOV_RADIUS)
        self.game_map.visible = visible
        self.game_map.mark_explored(visible)

    # ------------------------------------------------------------------
    # Spieleraktionen (eine Aktion = eine Runde)
    # ------------------------------------------------------------------
    def move_player(self, dx: int, dy: int) -> None:
        if self.game_over:
            return
        nx, ny = self.player.x + dx, self.player.y + dy
        if not self.game_map.is_walkable(nx, ny):
            return  # gegen die Wand – keine Runde verbraucht

        target = self.actor_at((nx, ny))
        if target is not None and target is not self.player:
            self._player_attack(target)
        else:
            self.player.pos = (nx, ny)
            self._pickup_items()
        self._end_turn()

    def drink_potion(self) -> None:
        if self.game_over:
            return
        if self.potions <= 0:
            self.add_message("Du hast keine Tränke.", config.COLOR_MSG_WARN)
            return
        if self.player.hp >= self.player.max_hp:
            self.add_message("Du bist bereits bei voller Gesundheit.", config.COLOR_MSG_WARN)
            return
        self.potions -= 1
        healed = self.player.heal(config.POTION_HEAL)
        self.add_message(f"Du trinkst einen Trank (+{healed} HP).", config.COLOR_MSG_GOOD)
        self._end_turn()

    def descend(self) -> None:
        if self.game_over:
            return
        if self.player.pos != self.game_map.stairs_down:
            self.add_message("Hier ist keine Treppe.", config.COLOR_MSG_WARN)
            return
        if self.dungeon_level >= config.DEPTH_GOAL:
            self.game_over = True
            self.won = True
            self.add_message("Die letzte Treppe führt ans Licht – du hast gewonnen!", config.COLOR_MSG_GOOD)
            return
        self.add_message("Du steigst tiefer in die Dunkelheit hinab …", config.COLOR_MSG_INFO)
        self._next_level()

    # ------------------------------------------------------------------
    # Kampf & Runden-Ende
    # ------------------------------------------------------------------
    def _player_attack(self, target: Actor) -> None:
        result = attack(self.player, target)
        if result.damage > 0:
            self.add_message(f"Du triffst {target.name} für {result.damage} Schaden.", config.COLOR_MSG_INFO)
        else:
            self.add_message(f"{target.name} wehrt deinen Angriff ab.", config.COLOR_MSG_WARN)
        if result.killed:
            self.add_message(f"{target.name} wurde besiegt!", config.COLOR_MSG_GOOD)
            self.entities.remove(target)

    def enemy_attack(self, attacker: Actor, defender: Actor) -> None:
        """Von der KI aufgerufen, wenn ein Gegner den Spieler angreift."""
        result = attack(attacker, defender)
        if result.damage > 0:
            self.add_message(f"{attacker.name} trifft dich für {result.damage} Schaden.", config.COLOR_MSG_BAD)
        else:
            self.add_message(f"Du wehrst {attacker.name} ab.", config.COLOR_MSG_INFO)
        if result.killed:
            self.game_over = True
            self.won = False
            self.add_message("Du stirbst in der Dunkelheit …", config.COLOR_MSG_BAD)

    def _pickup_items(self) -> None:
        for e in list(self.entities):
            if isinstance(e, Item) and e.pos == self.player.pos:
                self.potions += 1
                self.entities.remove(e)
                self.add_message(f"Du hebst einen {e.name} auf.", config.COLOR_MSG_GOOD)

    def _process_enemies(self) -> None:
        for entity in list(self.entities):
            if entity is self.player:
                continue
            if isinstance(entity, Actor) and entity.is_alive and entity.ai is not None:
                entity.ai.take_turn(entity, self)
                if self.game_over:
                    return

    def _end_turn(self) -> None:
        if self.game_over:
            return
        self._process_enemies()
        self.update_fov()

    def add_message(self, text: str, color: tuple[int, int, int]) -> None:
        self.messages.append((text, color))
        if len(self.messages) > 50:
            del self.messages[:-50]


# ----------------------------------------------------------------------
# Hauptschleife (pygame)
# ----------------------------------------------------------------------
def main() -> None:
    import pygame

    from .renderer import Renderer

    move_keys = {
        pygame.K_UP: (0, -1), pygame.K_w: (0, -1), pygame.K_k: (0, -1),
        pygame.K_DOWN: (0, 1), pygame.K_s: (0, 1), pygame.K_j: (0, 1),
        pygame.K_LEFT: (-1, 0), pygame.K_a: (-1, 0), pygame.K_h: (-1, 0),
        pygame.K_RIGHT: (1, 0), pygame.K_d: (1, 0), pygame.K_l: (1, 0),
    }

    renderer = Renderer()
    game = Game()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif game.game_over:
                    if event.key == pygame.K_r:
                        game = Game()
                elif event.key in move_keys:
                    game.move_player(*move_keys[event.key])
                elif event.key in (pygame.K_q, pygame.K_p):
                    game.drink_potion()
                elif event.key in (pygame.K_PERIOD, pygame.K_RETURN, pygame.K_GREATER):
                    game.descend()

        renderer.render(game)
        renderer.clock.tick(config.FPS)

    pygame.quit()
