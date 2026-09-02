from roguelike.game_map import GameMap, floor_tile, wall_tile
from roguelike.pathfinding import astar


def open_map(width=10, height=10):
    game_map = GameMap(width, height)
    for x in range(width):
        for y in range(height):
            game_map.set_tile(x, y, floor_tile())
    return game_map


def test_straight_path_length():
    game_map = open_map()
    path = astar(game_map, (0, 0), (0, 5))
    assert path[-1] == (0, 5)
    assert len(path) == 5


def test_same_start_and_goal():
    game_map = open_map()
    assert astar(game_map, (2, 2), (2, 2)) == []


def test_no_path_through_solid_rock():
    game_map = GameMap(5, 5)  # komplett Wand
    assert astar(game_map, (0, 0), (4, 4)) == []


def test_path_goes_around_wall():
    game_map = open_map(5, 5)
    for y in range(0, 4):  # Wand-Säule mit Lücke unten
        game_map.set_tile(2, y, wall_tile())
    path = astar(game_map, (0, 0), (4, 0))
    assert path and path[-1] == (4, 0)
    assert len(path) > 4  # muss außen herum


def test_blocked_tiles_are_avoided():
    game_map = open_map(5, 5)
    blocked = {(1, 0), (1, 1)}
    path = astar(game_map, (0, 0), (2, 0), blocked)
    assert path and path[-1] == (2, 0)
    assert not blocked.intersection(path)
