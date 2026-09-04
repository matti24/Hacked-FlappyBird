"""Misst die reine Render-Zeit pro Frame (Software/CPU) als FPS-Schaetzung.

Headless (SDL dummy) rendert per CPU wie auch WASM im Browser -> guter Proxy
fuer die Browser-Performance. Nur ein Entwickler-Werkzeug.
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

from neuroflap.renderer import Renderer  # noqa: E402
from neuroflap.simulation import Simulation  # noqa: E402


def main() -> None:
    sim = Simulation(random.Random(3))
    while sim.population.generation < 6:
        sim._step_ai()
    for _ in range(150):
        sim._step_ai()

    renderer = Renderer()
    frames = 400

    # nur Rendering messen
    t0 = time.perf_counter()
    for _ in range(frames):
        renderer.render(sim, speed=2, active=True)
    dt_render = time.perf_counter() - t0

    # Rendering + Simulation (2 Steps/Frame) zusammen = reales Frame-Budget
    t0 = time.perf_counter()
    for _ in range(frames):
        sim._step_ai()
        sim._step_ai()
        renderer.render(sim, speed=2, active=True)
    dt_full = time.perf_counter() - t0

    print(f"Nur Rendering : {dt_render/frames*1000:6.2f} ms/Frame  ->  {frames/dt_render:6.0f} FPS moeglich")
    print(f"Render + 2x Sim: {dt_full/frames*1000:6.2f} ms/Frame  ->  {frames/dt_full:6.0f} FPS moeglich")


if __name__ == "__main__":
    main()
