import random

from neuroflap.genetic import mutate, tournament_select, uniform_crossover


def test_crossover_keeps_length_and_uses_parents():
    a = [0.0] * 10
    b = [1.0] * 10
    child = uniform_crossover(a, b, random.Random(1))
    assert len(child) == 10
    assert all(gene in (0.0, 1.0) for gene in child)


def test_mutate_changes_every_gene_at_full_rate():
    genome = [0.0] * 20
    mutated = mutate(genome, 1.0, 0.5, random.Random(1))
    assert all(gene != 0.0 for gene in mutated)


def test_mutate_leaves_genome_untouched_at_zero_rate():
    genome = [1.0] * 20
    assert mutate(genome, 0.0, 0.5, random.Random(1)) == genome


def test_tournament_picks_fittest_candidate():
    scored = [(1.0, ["a"]), (5.0, ["b"]), (3.0, ["c"])]
    winner = tournament_select(scored, random.Random(1), k=3)
    assert winner == ["b"]
