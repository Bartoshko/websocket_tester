from math import sqrt, acos, cos, sin, floor
from copy import deepcopy
import numpy as np


def generate_path(points, speed, emitting_time_stamp):
    coordinates = []
    km_h_to_cm_s_scalar = 27.7778
    first = None
    for point in points:
        if first == None:
            start = np.array([point['x'], point['y']])
            first = True
        else:
            destination = np.array([point['x'], point['y']])
            distance = np.linalg.norm(destination - start)
            local_vector = (destination - start) * speed * km_h_to_cm_s_scalar * emitting_time_stamp / distance
            coord = deepcopy(start)
            coordinates.append(_coord_parse_as_object(coord))
            while _is_in_range(coord, start, destination):
                coord[0] += local_vector[0]
                coord[1] += local_vector[1]
                coordinates.append(_coord_parse_as_object(coord))
            start = deepcopy(destination)
    return coordinates


def _coord_parse_as_object(arr_coord):
    return {
        'x': arr_coord[0],
        'y': arr_coord[1],
        'z': 0
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
