from math import sqrt, acos, cos, sin, floor
from copy import deepcopy
import numpy as np


def generate_path(points, speed):
    def movement_vector_generator(start, finish, move_separation):
        x_length = finish['x'] - start['x']
        y_length = finish['y'] - start['y']
        z_length = finish['z'] - start['z']
        if x_length == 0 and y_length == 0 and z_length == 0:
            return 0, 0, 0
        if x_length == 0 and y_length == 0:
            return 0, 0, move_separation
        if x_length == 0 and z_length == 0:
            return 0, move_separation, 0
        if y_length == 0 and z_length == 0:
            return move_separation, 0, 0
        if x_length == 0:
            gradient_y, gradient_z = calculate_flat_gradient(y_length, z_length, move_separation)
            return 0, gradient_y, gradient_z
        if y_length == 0:
            gradient_x, gradient_z = calculate_flat_gradient(x_length, z_length, move_separation)
            return gradient_x, 0, gradient_z
        if z_length == 0:
            gradient_x, gradient_y = calculate_flat_gradient(x_length, y_length, move_separation)
            return gradient_x, gradient_y, 0
        return calculate_cubic_gradient(start, finish, x_length, y_length, move_separation)

    def calculate_flat_gradient(a, b, move_separation):
        section_scalar = sqrt(a ** 2 + b ** 2)
        arc_radians = acos(a / section_scalar)
        gradient_a = cos(arc_radians) * move_separation
        gradient_b = sin(arc_radians) * move_separation
        gradient_b = -gradient_b if gradient_b < 0 else gradient_b
        return gradient_a, gradient_b

    def calculate_cubic_gradient(start, finish, x_length, y_length, move_separation):
        section_scalar = np.linalg.norm(
            np.array(start['x'], start['y'], start['z']) -
            np.array(finish['x'], finish['y'], finish['z'])
        )
        arc_z_radians = acos(sqrt(x_length ** 2 + y_length ** 2) / section_scalar)
        gradient_x_y = cos(arc_z_radians) * move_separation
        gradient_z = sin(arc_z_radians) * move_separation
        gradient_z = -gradient_z if gradient_z < 0 else gradient_z
        arc_y_radians = acos(x_length / gradient_x_y)
        gradient_x = cos(arc_y_radians) * move_separation
        gradient_y = sin(arc_y_radians) * move_separation
        gradient_y = -gradient_y if gradient_y < 0 else gradient_y
        return gradient_x, gradient_y, gradient_z

    separation = speed
    coordinates = []
    for i in range(len(points) - 1):
        start_point = points[i]
        finish_point = points[i + 1]
        step_point_x = deepcopy(start_point['x'])
        step_point_y = deepcopy(start_point['y'])
        step_point_z = deepcopy(start_point['z'])
        coordinates.append({
            'x': step_point_x,
            'y': step_point_y,
            'z': step_point_z
        })
        section_vector = movement_vector_generator(start_point, finish_point, separation)
        sections = []
        if section_vector[0] != 0:
            sections.append((finish_point['x'] - start_point['x']) / section_vector[0])
        if section_vector[1] != 0:
            sections.append((finish_point['y'] - start_point['y']) / section_vector[1])
        if section_vector[2] != 0:
            sections.append((finish_point['z'] - start_point['z']) / section_vector[2])
        path_steps_in_section = floor(max(sections))
        while path_steps_in_section > 0:
            step_point_x += int(section_vector[0])
            step_point_y += int(section_vector[1])
            step_point_z += int(section_vector[2])
            coordinates.append(
                {
                    'x': deepcopy(step_point_x),
                    'y': deepcopy(step_point_y),
                    'z': deepcopy(step_point_z)
                }
            )
            path_steps_in_section -= 1
    return coordinates
