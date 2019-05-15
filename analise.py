import json
import numpy as np
from collections import Counter
from source.services.print_to_console import dashed_printer
import matplotlib.pyplot as plt
import sys
from random import randint


def get_separation_in_seconds(frame):
    if 'frame_time_separation' in frame.keys():
        time_separation = frame['frame_time_separation']
        if time_separation > 0:
            return time_separation
    return None


def get_size_in_bytes(frame):
    if 'frame_size_in_bytes' in frame.keys():
        size_in_bytes = frame['frame_size_in_bytes']
        return size_in_bytes
    return None


def calculate_mean(numbers):
    a_numbers = np.array(numbers)
    return np.mean(a_numbers)


def calculate_average(numbers):
    a_numbers = np.array(numbers)
    return np.average(a_numbers)


def get_most_common(numbers):
    counted = Counter(numbers)
    return counted.most_common()


def reject_outliers(numbers, m=3):
    a_numbers = np.array(numbers)
    return a_numbers[abs(a_numbers - np.mean(a_numbers)) < m * np.std(a_numbers)]


def sum_list_over_each_step(numbers):
    return [sum(numbers[0:i]) for i, _ in enumerate(numbers)]


def plot_histogram_measurements(measurements_per_frame):
    plt.hist(measurements_per_frame[1:], bins=100)
    plt.title('Measurements per frame histogram')
    plt.xlabel('Measurements number')
    plt.ylabel('Occurrence')
    plt.show()


def plot_histogram_separation_times(separation_times):
    plt.hist(separation_times[1:], bins=2)
    plt.title('Frame separation time histogram')
    plt.xlabel('Separation time number')
    plt.ylabel('Occurrence')
    plt.show()


def plot_separation_time(separation_times):
    plt.plot(separation_times, 'b+')
    plt.title('Separation time between consecutive frames')
    plt.ylabel('Time separation in seconds')
    plt.xlabel('Consecutive frame number')
    plt.show()

def plot_measurements_per_second(measurements_per_frame):
    plt.plot(measurements_per_frame, 'r+')
    plt.title('Measurements per frame')
    plt.ylabel('Number of measurements per frame')
    plt.xlabel('Consecutive frame number')
    plt.show()


def plot_separation_time_filtered(separation_time_filtered):
    plt.plot(separation_time_filtered, 'b+')
    plt.title('Separation time between consecutive frames with filtered outliers')
    plt.ylabel('Time separation in seconds')
    plt.xlabel('Consecutive frame number with standard deviation < 2')
    plt.show()


def plot_measurements_per_frame_filtered(measurements_per_frame_filtered):
    plt.plot(measurements_per_frame_filtered, 'r+')
    plt.title('Measurements per frame with filtered outliers')
    plt.ylabel('Number of measurements per frame')
    plt.xlabel('Consecutive frame number with standard deviation < 2')
    plt.show()

def plot_measurements_sum_over_all_steps(measurements_sum_over_all_steps):
    plt.plot(measurements_sum_over_all_steps, 'r+')
    plt.title('All collected measurements distribution in time.')
    plt.ylabel('Number of measurements')
    plt.xlabel('Consecutive frame number')
    plt.show()


def plot_relation(separation_times, measurements_per_frame):
    plt.plot(separation_times, measurements_per_frame, 'b+')
    plt.title('Relation between frame time separation and number of measurements')
    plt.ylabel('Number of measurements')
    plt.xlabel('Time separation in seconds')
    plt.show()


def print_to_console(measure_examples, separation_time_mean, measurement_per_frame_mean, sum_all_measurement, separation_times, measurements_per_frame, bandwidths):
    dashed_printer('ANALYTICAL DATA:')
    rand_index = randint(0, len(measure_examples) - 1)
    print('For randomly chosen index: {1} measures example: {0}'.format(measure_examples[rand_index], rand_index))
    dashed_printer('Statistical calculations:')
    print('Separation time mean: {0:.2f}'.format(separation_time_mean))
    print('Measurements per frame mean: {0:.2f}'.format(measurement_per_frame_mean))
    print('Number of measurements in all frames: {}'.format(sum_all_measurement))
    print('First frame: separation time {0:.2f} measurement per frame {0:2f}'
          .format(separation_times[0], measurements_per_frame[0]))
    print('Frames with separation time span under 1 second:')
    indexes_of_separation_under_one_sec = [i for i, v in enumerate(separation_times) if v < 1]
    print(indexes_of_separation_under_one_sec)
    for i in indexes_of_separation_under_one_sec:
        print('Value: {} second'.format(separation_times[i]))
    print('Frames with number of measurements over 50:')
    indexes_of_measurements_over_fifty = [i for i, v in enumerate(measurements_per_frame) if v >= 50]
    print(indexes_of_measurements_over_fifty)
    for i in indexes_of_separation_under_one_sec:
        print('Value: {} measurements per frame'.format(measurements_per_frame[i]))
    dashed_printer('Distribution: ')
    for bandwidth in bandwidths:
        print('Frame length: {} occurred {} times'.format(bandwidth[0], bandwidth[1]))


def analise(file_path):
    separation_times = []
    measurements_per_frame = []
    dists_ids_in_frame = []
    measure_examples = []
    with open(file_path, 'r') as f:
        for line in f:
            collection = json.loads(line)
            for item in collection:
                measures = json.loads(item['frame'])
                separation_times.append(item['frame_time_separation'])
                measurements_per_frame.append(len(measures))
                measure_examples.append(measures)
                dists_in_measurement = []
                for measure in measures:
                    dists_in_measurement.append([measure['did1'], measure['did1']])
                dists_ids_in_frame.append(dists_in_measurement)
    separation_time_mean = calculate_mean(separation_times)
    measurement_per_frame_mean = calculate_mean(measurements_per_frame)
    sum_all_measurement = sum(measurements_per_frame)
    separation_time_filtered = reject_outliers(separation_times)
    measurements_per_frame_filtered = reject_outliers(measurements_per_frame)
    measurements_sum_over_all_steps = sum_list_over_each_step(measurements_per_frame)
    bandwidths = get_most_common(measurements_per_frame)
    print_to_console(measure_examples, separation_time_mean, measurement_per_frame_mean, sum_all_measurement, separation_times, measurements_per_frame, bandwidths)
    plot_histogram_measurements(measurements_per_frame)
    plot_histogram_separation_times(separation_times)
    plot_separation_time(separation_times)
    plot_measurements_per_second(measurements_per_frame)
    plot_separation_time_filtered(separation_time_filtered)
    plot_measurements_per_frame_filtered(measurements_per_frame_filtered)
    plot_measurements_sum_over_all_steps(measurements_sum_over_all_steps)
    plot_relation(separation_times, measurements_per_frame)



if __name__ == '__main__':
    if len(sys.argv) == 2:
        file_path_from_argv = sys.argv[1]
        analise(file_path_from_argv)
