import math


def closest_power_of_two(number):
    closest_exponent = math.ceil(math.log2(number))

    closest_power = 2**closest_exponent

    return closest_power
