from roguelike.fov import compute_fov
from roguelike.game_map import GameMap, floor_tile, wall_tile


def open_map(width=15, height=15):
    game_map = GameMap(width, height)
    for x in range(width):
        for y in range(height):
            game_map.set_tile(x, y, floor_tile())
    return game_map


def test_origin_is_visible():
    game_map = open_map()
    assert (7, 7) in compute_fov(game_map, (7, 7), 5)


def test_far_tile_outside_radius_hidden():
    game_map = open_map()
    visible = compute_fov(game_map, (7, 7), 3)
    assert (7, 13) not in visible  # Distanz 6 > Radius 3


def test_wall_is_seen_but_blocks_behind():
    game_map = open_map()
    game_map.set_tile(8, 7, wall_tile())
    visible = compute_fov(game_map, (7, 7), 8)
    assert (8, 7) in visible       # die Wand selbst ist sichtbar
    assert (9, 7) not in visible   # direkt dahinter liegt im Schatten


def test_open_area_reveals_many_tiles():
    game_map = open_map()
    assert len(compute_fov(game_map, (7, 7), 8)) > 20
