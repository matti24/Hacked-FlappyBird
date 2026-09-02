import random

from roguelike.procgen import generate_dungeon


def _gen(seed):
    return generate_dungeon(
        58, 36, max_rooms=18, room_min_size=6, room_max_size=12, rng=random.Random(seed)
    )


def test_rooms_and_stairs_created():
    game_map, rooms = _gen(1)
    assert len(rooms) > 0
    assert game_map.stairs_down is not None


def test_generation_is_deterministic():
    _, rooms_a = _gen(42)
    _, rooms_b = _gen(42)
    assert [r.center for r in rooms_a] == [r.center for r in rooms_b]


def test_placed_rooms_do_not_overlap():
    _, rooms = _gen(7)
    for i, a in enumerate(rooms):
        for b in rooms[i + 1:]:
            assert not a.intersects(b)


def test_stairs_are_walkable():
    game_map, _ = _gen(3)
    sx, sy = game_map.stairs_down
    assert game_map.is_walkable(sx, sy)


def test_dungeon_has_open_space():
    game_map, _ = _gen(5)
    walkable = sum(
        1
        for x in range(game_map.width)
        for y in range(game_map.height)
        if game_map.tiles[x][y].walkable
    )
    assert walkable > 50
