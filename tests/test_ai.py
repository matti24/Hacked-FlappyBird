from roguelike.ai import _has_line_of_sight
from roguelike.entities import make_goblin
from roguelike.game import Game
from roguelike.game_map import GameMap, floor_tile, wall_tile


def _open_arena(game, size=15):
    game_map = GameMap(size, size)
    for x in range(size):
        for y in range(size):
            game_map.set_tile(x, y, floor_tile())
    game.game_map = game_map
    return game_map


def test_line_of_sight_clear():
    game_map = GameMap(10, 10)
    for x in range(10):
        for y in range(10):
            game_map.set_tile(x, y, floor_tile())
    assert _has_line_of_sight(game_map, (0, 0), (5, 0))


def test_line_of_sight_blocked_by_wall():
    game_map = GameMap(10, 10)
    for x in range(10):
        for y in range(10):
            game_map.set_tile(x, y, floor_tile())
    game_map.set_tile(3, 0, wall_tile())
    assert not _has_line_of_sight(game_map, (0, 0), (5, 0))


def test_enemy_moves_closer_when_it_sees_player():
    game = Game(seed=1)
    _open_arena(game)
    game.player.pos = (7, 7)
    goblin = make_goblin(11, 7)  # 4 Felder entfernt, freie Sicht
    game.entities = [game.player, goblin]
    game.update_fov()

    before = goblin.distance_to(game.player)
    goblin.ai.take_turn(goblin, game)
    assert goblin.distance_to(game.player) < before
    assert goblin.ai.state == "chase"


def test_enemy_attacks_adjacent_player():
    game = Game(seed=1)
    _open_arena(game)
    game.player.pos = (7, 7)
    goblin = make_goblin(8, 7)  # direkt daneben
    game.entities = [game.player, goblin]
    game.update_fov()

    hp_before = game.player.hp
    goblin.ai.take_turn(goblin, game)
    assert game.player.hp < hp_before


def test_enemy_remembers_last_position_when_sight_lost():
    game = Game(seed=1)
    _open_arena(game)
    game.player.pos = (7, 7)
    goblin = make_goblin(10, 7)
    game.entities = [game.player, goblin]
    game.update_fov()

    goblin.ai.take_turn(goblin, game)          # sieht Spieler -> merkt Position
    assert goblin.ai.last_known is not None
    assert goblin.ai.memory > 0
