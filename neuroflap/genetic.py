"""Operatoren des genetischen Algorithmus: Selektion, Crossover, Mutation."""

from __future__ import annotations

import random


def uniform_crossover(genome_a: list[float], genome_b: list[float], rng: random.Random) -> list[float]:
    """Kombiniert zwei Eltern-Genome gengenau (je Gen zufällig ein Elternteil)."""
    return [a if rng.random() < 0.5 else b for a, b in zip(genome_a, genome_b)]


def mutate(genome: list[float], rate: float, strength: float, rng: random.Random) -> list[float]:
    """Verändert einzelne Gene: meist kleine gaßsche Schritte, selten ein Neustart.

    Der gelegentliche Voll-Reset (~10 %) sorgt für Exploration, ohne die
    bewährten Gewichte der Eltern flächig zu zerstören.
    """
    out: list[float] = []
    for gene in genome:
        if rng.random() < rate:
            if rng.random() < 0.1:
                out.append(rng.gauss(0.0, 1.0))
            else:
                out.append(gene + rng.gauss(0.0, strength))
        else:
            out.append(gene)
    return out


def tournament_select(
    scored: list[tuple[float, list[float]]],
    rng: random.Random,
    k: int = 3,
) -> list[float]:
    """Wählt aus k zufälligen Kandidaten das fitteste Genom aus."""
    k = min(k, len(scored))
    contenders = rng.sample(scored, k)
    best = max(contenders, key=lambda item: item[0])
    return best[1]
