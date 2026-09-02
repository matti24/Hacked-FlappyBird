from roguelike.entities import Actor, make_goblin
from roguelike.game import Game


def test_new_game_state():
    game = Game(seed=1)
    assert game.dungeon_level == 1
    assert game.player in game.entities
    assert not game.game_over


def test_game_is_deterministic_with_seed():
    a = Game(seed=123)
    b = Game(seed=123)
    assert a.player.pos == b.player.pos
    assert [type(e).__name__ for e in a.entities] == [type(e).__name__ for e in b.entities]


def test_walking_into_wall_keeps_position():
    game = Game(seed=1)
    px, py = game.player.pos
    # Richtung suchen, die auf eine Wand zeigt
    for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
        if not game.game_map.is_walkable(px + dx, py + dy):
            game.move_player(dx, dy)
            assert game.player.pos == (px, py)
            return


def test_player_kills_weak_adjacent_monster():
    game = Game(seed=1)
    px, py = game.player.pos
    for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
        if game.game_map.is_walkable(px + dx, py + dy) and game.actor_at((px + dx, py + dy)) is None:
            goblin = make_goblin(px + dx, py + dy)
            goblin.hp = 1  # ein Treffer genügt
            game.entities.append(goblin)
            game.move_player(dx, dy)
            assert goblin not in game.entities  # besiegt und entfernt
            return


def test_drinking_without_potions_does_nothing():
    game = Game(seed=1)
    game.potions = 0
    hp = game.player.hp
    game.drink_potion()
    assert game.player.hp == hp


def test_potion_heals_player():
    game = Game(seed=1)
    game.potions = 1
    game.player.hp = 5
    game.drink_potion()
    assert game.player.hp > 5
    assert game.potions == 0
