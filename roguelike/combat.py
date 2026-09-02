"""Kampfauflösung zwischen zwei Wesen."""

from __future__ import annotations

from dataclasses import dataclass

from .entities import Actor


@dataclass
class AttackResult:
    attacker: str
    defender: str
    damage: int
    killed: bool


def attack(attacker: Actor, defender: Actor) -> AttackResult:
    """Führt einen Angriff aus und wendet den Schaden direkt an."""
    damage = max(0, attacker.power - defender.defense)
    defender.take_damage(damage)
    return AttackResult(
        attacker=attacker.name,
        defender=defender.name,
        damage=damage,
        killed=not defender.is_alive,
    )
