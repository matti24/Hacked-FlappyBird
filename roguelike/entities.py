"""Spielobjekte: Spieler, Monster und Items."""

from __future__ import annotations

from .ai import HostileAI


class Entity:
    """Alles, was auf der Karte steht (Wesen oder Gegenstand)."""

    def __init__(
        self,
        x: int,
        y: int,
        char: str,
        color: tuple[int, int, int],
        name: str,
        *,
        blocks_movement: bool = True,
    ) -> None:
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.name = name
        self.blocks_movement = blocks_movement

    @property
    def pos(self) -> tuple[int, int]:
        return (self.x, self.y)

    @pos.setter
    def pos(self, value: tuple[int, int]) -> None:
        self.x, self.y = value

    def move(self, dx: int, dy: int) -> None:
        self.x += dx
        self.y += dy

    def distance_to(self, other: "Entity") -> int:
        """Chebyshev-Distanz (diagonale Nähe zählt als 1)."""
        return max(abs(self.x - other.x), abs(self.y - other.y))


class Actor(Entity):
    """Ein kampffähiges Wesen mit Lebenspunkten und optionaler KI."""

    def __init__(
        self,
        x: int,
        y: int,
        char: str,
        color: tuple[int, int, int],
        name: str,
        *,
        hp: int,
        power: int,
        defense: int,
        ai: HostileAI | None = None,
    ) -> None:
        super().__init__(x, y, char, color, name, blocks_movement=True)
        self.max_hp = hp
        self.hp = hp
        self.power = power
        self.defense = defense
        self.ai = ai

    @property
    def is_alive(self) -> bool:
        return self.hp > 0

    def take_damage(self, amount: int) -> None:
        self.hp = max(0, self.hp - amount)

    def heal(self, amount: int) -> int:
        before = self.hp
        self.hp = min(self.max_hp, self.hp + amount)
        return self.hp - before


class Item(Entity):
    """Ein aufsammelbarer Gegenstand (blockiert die Bewegung nicht)."""

    def __init__(self, x: int, y: int, char: str, color: tuple[int, int, int], name: str, *, heal_amount: int) -> None:
        super().__init__(x, y, char, color, name, blocks_movement=False)
        self.heal_amount = heal_amount


# --- Fabrikfunktionen ---------------------------------------------------

def make_player(x: int, y: int) -> Actor:
    return Actor(x, y, "@", (120, 230, 180), "Held", hp=30, power=5, defense=1)


def make_goblin(x: int, y: int) -> Actor:
    return Actor(x, y, "g", (120, 190, 95), "Kobold", hp=8, power=3, defense=0, ai=HostileAI())


def make_orc(x: int, y: int) -> Actor:
    return Actor(x, y, "o", (95, 150, 75), "Ork", hp=16, power=4, defense=1, ai=HostileAI())


def make_troll(x: int, y: int) -> Actor:
    return Actor(x, y, "T", (205, 95, 95), "Troll", hp=30, power=6, defense=2, ai=HostileAI())


def make_potion(x: int, y: int) -> Item:
    return Item(x, y, "!", (215, 110, 220), "Heiltrank", heal_amount=8)
