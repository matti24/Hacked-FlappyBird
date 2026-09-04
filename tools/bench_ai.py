"""Headless-Benchmark: wie schnell/gut lernt die KI? (ohne Rendering)

Startet die reine Simulation ueber mehrere Generationen und protokolliert den
besten Score je Runde sowie die Simulationsgeschwindigkeit (Steps/Sekunde).
Nur ein Entwickler-Werkzeug, nicht Teil des Spiels.
"""
from __future__ import annotations

import os
import random
import sys
import time

os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from neuroflap.simulation import Simulation  # noqa: E402


def evaluate(generations: int, seed: int) -> tuple[list[tuple[int, int]], int, float]:
    sim = Simulation(random.Random(seed))
    history: list[tuple[int, int]] = []
    round_peak = 0
    steps = 0
    t0 = time.perf_counter()
    while sim.population.generation <= generations:
        prev_gen = sim.population.generation
        sim._step_ai()
        steps += 1
        round_peak = max(round_peak, sim.current_score())
        if sim.population.generation != prev_gen:
            history.append((prev_gen, round_peak))
            round_peak = 0
    dt = time.perf_counter() - t0
    return history, steps, dt


def main() -> None:
    for seed in (1, 7, 42):
        hist, steps, dt = evaluate(35, seed)
        best = max((s for _, s in hist), default=0)
        # erste Generation, die Score >= 20 schafft
        solved = next((g for g, s in hist if s >= 20), None)
        print(f"--- Seed {seed} ---")
        line = "  ".join(f"G{g}:{s}" for g, s in hist[:18])
        print(f"  Verlauf: {line}")
        print(f"  Bester Score: {best} | Score>=20 ab Generation: {solved}")
        print(f"  Speed: {steps} Steps in {dt:.2f}s = {steps/dt:,.0f} steps/s\n")


if __name__ == "__main__":
    main()
