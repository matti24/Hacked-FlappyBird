"""Verwaltet die Vogel-Population und die Evolution zwischen den Generationen."""

from __future__ import annotations

import random

from . import config
from .bird import Bird
from .genetic import mutate, tournament_select, uniform_crossover
from .neural_net import NeuralNetwork


def _new_brain(rng: random.Random) -> NeuralNetwork:
    return NeuralNetwork(config.INPUT_SIZE, config.HIDDEN_SIZE, config.OUTPUT_SIZE, rng)


def _brain_from_genome(genome: list[float]) -> NeuralNetwork:
    return NeuralNetwork.from_genome(
        genome, config.INPUT_SIZE, config.HIDDEN_SIZE, config.OUTPUT_SIZE
    )


class Population:
    def __init__(self, rng: random.Random | None = None) -> None:
        self.rng = rng or random.Random()
        self.generation = 1
        self.best_score_ever = 0
        self.best_fitness_ever = 0.0
        self.last_best_fitness = 0.0
        self.fitness_history: list[float] = []
        self.birds = [Bird(_new_brain(self.rng)) for _ in range(config.POPULATION_SIZE)]

    def alive_birds(self) -> list[Bird]:
        return [b for b in self.birds if b.alive]

    def all_dead(self) -> bool:
        return not any(b.alive for b in self.birds)

    def best_alive(self) -> Bird | None:
        alive = self.alive_birds()
        if not alive:
            return None
        return max(alive, key=lambda b: b.fitness)

    def evolve(self) -> None:
        """Bildet aus den fittesten Netzen die nächste Generation."""
        scored = [(b.fitness, b.brain.genome()) for b in self.birds]
        scored.sort(key=lambda item: item[0], reverse=True)

        best_fitness = scored[0][0]
        best_score = max(b.score for b in self.birds)
        self.last_best_fitness = best_fitness
        self.best_fitness_ever = max(self.best_fitness_ever, best_fitness)
        self.best_score_ever = max(self.best_score_ever, best_score)
        self.fitness_history.append(best_fitness)

        new_brains: list[NeuralNetwork] = []

        # Elite unverändert übernehmen.
        for i in range(min(config.ELITE_COUNT, len(scored))):
            new_brains.append(_brain_from_genome(list(scored[i][1])))

        # Rest durch Selektion, Crossover und Mutation erzeugen.
        while len(new_brains) < config.POPULATION_SIZE:
            parent_a = tournament_select(scored, self.rng)
            parent_b = tournament_select(scored, self.rng)
            child = uniform_crossover(parent_a, parent_b, self.rng)
            child = mutate(child, config.MUTATION_RATE, config.MUTATION_STRENGTH, self.rng)
            new_brains.append(_brain_from_genome(child))

        self.birds = [Bird(brain) for brain in new_brains]
        self.generation += 1
