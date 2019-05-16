from math import sqrt, acos, cos, sin, floor
from copy import deepcopy
import numpy as np


def generate_path(points, speed):
    coordinates = []
    first = None
    for point in points:
        if first == None:
            start = np.array([point['x'], point['y']])
            first = True
        else:
            destination = np.array([point['x'], point['y']])
            local_vector = (destination - start) / speed
            coord = start
            coordinates.append(coord_parse(coord))
            while abs(destination[0]) - abs(coord[0]) > abs(local_vector[0]) and \
                abs(destination[1]) - abs(coord[1]) > abs(local_vector[1]):
                coord[0] += local_vector[0]
                coord[1] += local_vector[1]
                coordinates.append(coord_parse(coord))
            start = deepcopy(destination)
    return coordinates


def coord_parse(arr_coord):
    return {
        'x': arr_coord[0],
        'y': arr_coord[1]
    }