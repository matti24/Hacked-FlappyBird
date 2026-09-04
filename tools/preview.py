"""Rendert je einen Screenshot (KI- und Mensch-Modus) headless als PNG.

Nur ein Entwickler-Werkzeug, um das Design ohne echtes Fenster zu pruefen.
"""
from __future__ import annotations

import os
import random
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame  # noqa: E402

from neuroflap.renderer import Renderer  # noqa: E402
from neuroflap.simulation import Simulation  # noqa: E402


def build_ai_state(seed: int = 3) -> Simulation:
    sim = Simulation(random.Random(seed))
    # ein paar Generationen lernen lassen (fuellt Fitness-Graph + gutes Netz)
    while sim.population.generation < 7:
        sim._step_ai()
    # mitten in einer Runde: viele Voegel leben, Score schon > 0
    for _ in range(260):
        sim._step_ai()
    return sim


def main() -> None:
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "build")
    os.makedirs(out, exist_ok=True)

    sim = build_ai_state()
    renderer = Renderer()
    renderer.render(sim, speed=2, active=True)
    ai_path = os.path.normpath(os.path.join(out, "preview_ai.png"))
    pygame.image.save(renderer.screen, ai_path)
    print("KI-Preview:", ai_path, "| Generation", sim.population.generation, "| Score", sim.current_score())

    # Mensch-Modus
    sim.set_mode("human")
    for _ in range(80):
        sim.step()
    renderer.render(sim, speed=1, active=True)
    hu_path = os.path.normpath(os.path.join(out, "preview_human.png"))
    pygame.image.save(renderer.screen, hu_path)
    print("Mensch-Preview:", hu_path)


if __name__ == "__main__":
    main()
