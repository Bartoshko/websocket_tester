import sys

import matplotlib.pyplot as plt
from source.services.path_generator import generate_path
from source.utils.data_setter import get_settings



def plot_path():
    if len(sys.argv) > 1:
        config_file_path = sys.argv[1]
    else:
        config_file_path = 'paths/default.json'
    path_configuration = get_settings(config_file_path)
    coordinates_configs = path_configuration['path']['coordinates']
    coordinates = []
    for point in coordinates_configs:
        coordinates.append(point)

    speed = path_configuration['path']['parameters']['speed']
    closed = path_configuration['path']['parameters']['closed']
    if closed:
        coordinates.append(coordinates[0])
    else:
        right_coordinates = list(coordinates)
        right_coordinates.reverse()
        coordinates += right_coordinates[1:len(right_coordinates)]
    print(coordinates)
    path = generate_path(coordinates, speed)
    for i, point in enumerate(path):
        print('number: {} point: {}'.format(i, point))
    x = []
    y = []
    for coord in path:
        x.append(coord['x'])
        y.append(coord['y'])
    plt.figure()
    plt.plot(x, y, 'ro')
    plt.legend(['Cross Point Coordinates'])
    plt.title('Tag walk simulation path.')
    plt.show()


if __name__ == '__main__':
    plot_path()
