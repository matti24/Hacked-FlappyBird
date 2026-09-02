import random

from neuroflap import config
from neuroflap.simulation import Simulation


def test_population_has_configured_size():
    sim = Simulation(random.Random(1))
    assert len(sim.population.birds) == config.POPULATION_SIZE


def test_step_runs_without_error():
    sim = Simulation(random.Random(1))
    for _ in range(20):
        sim.step()


def test_evolve_advances_generation_and_keeps_size():
    sim = Simulation(random.Random(1))
    gen = sim.population.generation
    sim.population.evolve()
    assert sim.population.generation == gen + 1
    assert len(sim.population.birds) == config.POPULATION_SIZE


def test_population_evolves_over_time():
    sim = Simulation(random.Random(1))
    start = sim.population.generation
    for _ in range(3000):
        sim.step()
    assert sim.population.generation > start


def test_bird_dies_when_leaving_screen():
    sim = Simulation(random.Random(1))
    bird = sim.population.birds[0]
    bird.y = -100
    sim.step()
    assert not bird.alive


def test_initial_pipes_present():
    sim = Simulation(random.Random(1))
    assert len(sim.pipes) >= 2
