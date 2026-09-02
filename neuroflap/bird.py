"""Ein KI-Vogel: Physik plus eigenes neuronales Netz als Steuerung."""

from __future__ import annotations

from . import config
from .neural_net import NeuralNetwork


class Bird:
    def __init__(self, brain: NeuralNetwork) -> None:
        self.y = config.HEIGHT / 2
        self.velocity = 0.0
        self.alive = True
        self.fitness = 0.0
        self.score = 0          # Anzahl passierter Röhren
        self.brain = brain

    def flap(self) -> None:
        self.velocity = config.FLAP_STRENGTH

    def update(self) -> None:
        self.velocity = min(self.velocity + config.GRAVITY, config.MAX_FALL_SPEED)
        self.y += self.velocity

    def decide(self, inputs: list[float]) -> None:
        """Lässt das Netz entscheiden, ob geflattert wird."""
        if self.brain.forward(inputs)[0] > 0.5:
            self.flap()
