import random

from neuroflap.neural_net import NeuralNetwork


def test_forward_output_size_and_range():
    net = NeuralNetwork(5, 8, 1, random.Random(1))
    out = net.forward([0.1] * 5)
    assert len(out) == 1
    assert 0.0 <= out[0] <= 1.0


def test_genome_length_matches():
    net = NeuralNetwork(5, 8, 1, random.Random(3))
    assert len(net.genome()) == net.genome_length
    assert net.genome_length == 5 * 8 + 8 + 8 * 1 + 1  # = 57


def test_genome_roundtrip_preserves_behaviour():
    net = NeuralNetwork(5, 8, 1, random.Random(2))
    genome = net.genome()
    clone = NeuralNetwork.from_genome(genome, 5, 8, 1)
    assert clone.genome() == genome
    assert clone.forward([0.2] * 5) == net.forward([0.2] * 5)


def test_same_seed_gives_same_network():
    a = NeuralNetwork(5, 8, 1, random.Random(42)).genome()
    b = NeuralNetwork(5, 8, 1, random.Random(42)).genome()
    assert a == b


def test_activations_recorded_for_visualisation():
    net = NeuralNetwork(5, 8, 1, random.Random(1))
    net.forward([0.5] * 5)
    assert len(net.last_hidden) == 8
    assert len(net.last_output) == 1
