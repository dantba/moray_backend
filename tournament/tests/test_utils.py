import pytest
from tournament.utils import closest_power_of_two


def test_closest_power_of_two():
    assert closest_power_of_two(1) == 1
    assert closest_power_of_two(2) == 2
    assert closest_power_of_two(4) == 4
    assert closest_power_of_two(8) == 8

    assert closest_power_of_two(3) == 4
    assert closest_power_of_two(5) == 8
    assert closest_power_of_two(6) == 8
    assert closest_power_of_two(7) == 8
