"""Ein kleines Feedforward-Netz – ohne externe ML-Bibliothek.

Aufbau: Eingabe → verborgene Schicht (tanh) → Ausgabe (sigmoid).
Die Gewichte lassen sich als flache Liste (Genom) exportieren/importieren,
damit der genetische Algorithmus damit rechnen kann.
"""

from __future__ import annotations

import math
import random


def _sigmoid(x: float) -> float:
    if x < -60.0:
        return 0.0
    if x > 60.0:
        return 1.0
    return 1.0 / (1.0 + math.exp(-x))


class NeuralNetwork:
    def __init__(
        self,
        input_size: int,
        hidden_size: int,
        output_size: int,
        rng: random.Random | None = None,
    ) -> None:
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.output_size = output_size
        rng = rng or random.Random()

        # Gewichte + Bias mit kleinen Zufallswerten initialisieren.
        self.w1 = [[rng.gauss(0, 1) for _ in range(input_size)] for _ in range(hidden_size)]
        self.b1 = [rng.gauss(0, 1) for _ in range(hidden_size)]
        self.w2 = [[rng.gauss(0, 1) for _ in range(hidden_size)] for _ in range(output_size)]
        self.b2 = [rng.gauss(0, 1) for _ in range(output_size)]

        # Letzte Aktivierungen für die Visualisierung.
        self.last_input: list[float] = [0.0] * input_size
        self.last_hidden: list[float] = [0.0] * hidden_size
        self.last_output: list[float] = [0.0] * output_size

    def forward(self, inputs: list[float]) -> list[float]:
        self.last_input = list(inputs)

        hidden = []
        for j in range(self.hidden_size):
            total = self.b1[j]
            row = self.w1[j]
            for i in range(self.input_size):
                total += row[i] * inputs[i]
            hidden.append(math.tanh(total))
        self.last_hidden = hidden

        outputs = []
        for k in range(self.output_size):
            total = self.b2[k]
            row = self.w2[k]
            for j in range(self.hidden_size):
                total += row[j] * hidden[j]
            outputs.append(_sigmoid(total))
        self.last_output = outputs
        return outputs

    # --- Genom-Konvertierung (für den genetischen Algorithmus) ---
    def genome(self) -> list[float]:
        flat: list[float] = []
        for row in self.w1:
            flat.extend(row)
        flat.extend(self.b1)
        for row in self.w2:
            flat.extend(row)
        flat.extend(self.b2)
        return flat

    @classmethod
    def from_genome(
        cls,
        genome: list[float],
        input_size: int,
        hidden_size: int,
        output_size: int,
    ) -> "NeuralNetwork":
        net = cls.__new__(cls)
        net.input_size = input_size
        net.hidden_size = hidden_size
        net.output_size = output_size

        idx = 0
        net.w1 = []
        for _ in range(hidden_size):
            net.w1.append(genome[idx: idx + input_size])
            idx += input_size
        net.b1 = genome[idx: idx + hidden_size]
        idx += hidden_size
        net.w2 = []
        for _ in range(output_size):
            net.w2.append(genome[idx: idx + hidden_size])
            idx += hidden_size
        net.b2 = genome[idx: idx + output_size]
        idx += output_size

        net.last_input = [0.0] * input_size
        net.last_hidden = [0.0] * hidden_size
        net.last_output = [0.0] * output_size
        return net

    @property
    def genome_length(self) -> int:
        return (
            self.hidden_size * self.input_size
            + self.hidden_size
            + self.output_size * self.hidden_size
            + self.output_size
        )
