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


def test_difficulty_increases_with_score():
    sim = Simulation(random.Random(1))
    assert sim.difficulty_gap(0) > sim.difficulty_gap(20)      # Lücke wird enger
    assert sim.difficulty_speed(0) < sim.difficulty_speed(20)  # Tempo steigt


def test_difficulty_is_capped():
    sim = Simulation(random.Random(1))
    assert sim.difficulty_gap(10_000) == config.PIPE_GAP_MIN
    assert sim.difficulty_speed(10_000) == config.PIPE_SPEED + config.PIPE_SPEED_MAX_BONUS


def test_switch_to_human_mode_creates_player():
    sim = Simulation(random.Random(1))
    sim.set_mode("human")
    assert sim.mode == "human"
    assert sim.player is not None
    assert sim.human_score == 0
    assert not sim.human_dead


def test_player_flap_sets_upward_velocity():
    sim = Simulation(random.Random(1))
    sim.set_mode("human")
    sim.player.velocity = 5.0
    sim.player_flap()
    assert sim.player.velocity == config.FLAP_STRENGTH


def test_human_dies_when_leaving_screen():
    sim = Simulation(random.Random(1))
    sim.set_mode("human")
    sim.player.y = -100
    sim.step()
    assert sim.human_dead


def test_flap_after_death_restarts_round():
    sim = Simulation(random.Random(1))
    sim.set_mode("human")
    sim.human_dead = True
    sim.player_flap()
    assert not sim.human_dead
    assert sim.human_score == 0


def test_center_bonus_adds_fitness():
    """Ein zentral in der Lücke fliegender Vogel sammelt Zusatz-Fitness."""
    sim = Simulation(random.Random(1))
    for other in sim.population.birds[1:]:
        other.alive = False
    bird = sim.population.birds[0]
    pipe = sim._next_pipe()
    assert pipe is not None
    bird.y = pipe.gap_y          # genau in der Mitte der Lücke
    bird.velocity = 0.0
    bird.fitness = 0.0
    sim._step_ai()
    # Basis-Überlebensbonus (1.0) plus Zentrierungsbonus (> 0)
    assert bird.fitness > 1.0


def test_round_ends_at_frame_limit(monkeypatch):
    """Auch wenn Vögel unsterblich wären, wechselt die Runde beim Frame-Limit."""
    monkeypatch.setattr(config, "MAX_ROUND_FRAMES", 5)
    sim = Simulation(random.Random(1))
    # Kollisionen ausschalten, damit niemand am Rand/Rohr stirbt.
    for bird in sim.population.birds:
        bird.update = lambda: None  # type: ignore[method-assign]
    for pipe in sim.pipes:
        pipe.collides_with = lambda _y: False  # type: ignore[method-assign]
    start_gen = sim.population.generation
    for _ in range(6):
        sim.step()
    assert sim.population.generation > start_gen
