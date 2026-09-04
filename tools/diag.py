"""Zerlegt die Frame-Kosten bei VOLLER Population (Gen 1, alle Voegel leben).

Trennt NN-Forward (reines Python, in WASM langsam) von Rendering (SDL, nativ),
um den echten Flaschenhals zu finden. Entwickler-Werkzeug.
"""
from __future__ import annotations

import os
import random
import sys
import time

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame  # noqa: E402

from neuroflap import config  # noqa: E402
from neuroflap.renderer import Renderer  # noqa: E402
from neuroflap.simulation import Simulation  # noqa: E402


def main() -> None:
    sim = Simulation(random.Random(1))  # Gen 1: alle POPULATION_SIZE Voegel leben
    alive = len(sim.population.alive_birds())
    pipe = sim._next_pipe()
    reps = 300

    # 1) NN-Forward fuer alle lebenden Voegel
    t0 = time.perf_counter()
    for _ in range(reps):
        for b in sim.population.birds:
            b.brain.forward(sim._inputs_for(b, pipe))
    t_nn = (time.perf_counter() - t0) / reps * 1000

    # 2) Kollisionspruefung fuer alle lebenden Voegel
    t0 = time.perf_counter()
    for _ in range(reps):
        for b in sim.population.birds:
            for p in sim.pipes:
                p.collides_with(b.y)
    t_col = (time.perf_counter() - t0) / reps * 1000

    # 3) Rendering bei voller Population
    renderer = Renderer()
    t0 = time.perf_counter()
    for _ in range(reps):
        renderer.render(sim, 1, True)
    t_render = (time.perf_counter() - t0) / reps * 1000

    print(f"Population: {config.POPULATION_SIZE}, lebende Voegel: {alive}, Pipes: {len(sim.pipes)}")
    print(f"  NN-Forward (alle Voegel): {t_nn:6.3f} ms")
    print(f"  Kollision  (alle Voegel): {t_col:6.3f} ms")
    print(f"  Rendering  (voll)       : {t_render:6.3f} ms")
    print(f"  => Desktop Frame @ speed2: {2*(t_nn+t_col)+t_render:6.3f} ms")
    print(f"  Anteil Sim(NN+Kol)*2 am Frame: {200*(t_nn+t_col)/(2*(t_nn+t_col)+t_render):.0f}%")


if __name__ == "__main__":
    main()
