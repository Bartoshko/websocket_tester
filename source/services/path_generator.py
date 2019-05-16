from math import sqrt, acos, cos, sin, floor
from copy import deepcopy
import numpy as np


def generate_path(points, speed, emiting_time_stamp):
    coordinates = []
    first = None
    for point in points:
        if first == None:
            start = np.array([point['x'], point['y']])
            first = True
        else:
            destination = np.array([point['x'], point['y']])
            distance = np.linalg.norm(destination - start)
            local_vector = (destination - start) / distance * speed * emiting_time_stamp * 100
            coord = deepcopy(start)
            coordinates.append(_coord_parse(coord))
            while _is_in_range(coord, start, destination):
                coord[0] += local_vector[0]
                coord[1] += local_vector[1]
                coordinates.append(_coord_parse(coord))
            start = deepcopy(destination)
            print(distance / len(coordinates))
    print(len(coordinates))
    return coordinates


def _coord_parse(arr_coord):
    return {
        'x': arr_coord[0],
        'y': arr_coord[1]
    }

def _is_in_range(point, border_a, border_b):
    x_in_range = False
    y_in_range = False
    if border_a[0] > border_b[0]:
        x_in_range = int(point[0]) in range(border_b[0] - 1, border_a[0] + 1)
    else:
        x_in_range = int(point[0]) in range(border_a[0] - 1, border_b[0] + 1)
    if border_a[1] > border_b[1]:
        y_in_range = int(point[1]) in range(border_b[1] - 1, border_a[1] + 1)
    else:
        y_in_range = int(point[1]) in range(border_a[1] - 1, border_b[1] + 1)
    return x_in_range and y_in_range
