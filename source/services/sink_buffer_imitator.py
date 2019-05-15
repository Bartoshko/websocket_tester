from random import randint, uniform
from source.utils.frame import frame_builder
import numpy as np


class SinkBuffer:
    __noise = 20
    __bandwidths_length = []
    __probabilities = []
    __probabilities_range = 0
    __noise_allowed = True

    @staticmethod
    def package_setter(i, j):
        id_0 = i['id']
        id_1 = j['id']
        distance = np.linalg.norm(
            np.array([i['x'], i['y'], i['z']]) -
            np.array([j['x'], j['y'], j['z']])
        )
        return id_0, id_1, distance

    def __init__(self, anchors):
        self.__anchors = anchors
        self.__ranges = []

    @property
    def noise(self):
        return self.__noise

    @noise.setter
    def noise(self, noise):
        if noise in range(0, 100):
            self.__noise_allowed = True
            self.__noise = noise
        else:
            raise Exception('Wrong noise probability value passed to Sink_Buffer')

    @property
    def bandwidths(self):
        bandwidths = []
        for probability, bandwidth in zip(self.__probabilities, self.__bandwidths_length):
            bandwidths.append((bandwidth, probability))
        return bandwidths

    @bandwidths.setter
    def bandwidths(self, bandwidths):
        exception_info = 'Wrong bandwidth passed to Sink_Buffer'
        if (type(bandwidths) is list or type(bandwidths) is tuple) and len(bandwidths) > 0:
            for bandwidth in bandwidths:
                if type(bandwidth) is not list and type(bandwidth) is not tuple:
                    raise Exception(exception_info)
            self.__noise_allowed = False
            bandwidths_sorted = sorted(bandwidths, key=lambda b: b[1])
            for bandwidth in bandwidths_sorted:
                self.__bandwidths_length.append(bandwidth[0])
                self.__probabilities.append(bandwidth[1])
            self.__probabilities_range = sum(self.__probabilities)
            range_stop = 0
            for probability in self.__probabilities:
                range_stop = (range_stop + probability / self.__probabilities_range)
                self.__ranges.append(range_stop)
        else:
            raise Exception(exception_info)

    def generate_buffer(self, tags):
        collection = []
        for i, anchor_0 in enumerate(self.__anchors):
            measurements = []
            if i < len(self.__anchors) - 1:
                anchor_measurements = (SinkBuffer.package_setter(anchor_0, anchor_1) for _, anchor_1 in
                                       enumerate(self.__anchors[i + 1:]))
                for anchor_measurement in anchor_measurements:
                    if not self.__get_simulated_noise():
                        measurements.append(frame_builder(*anchor_measurement))
            tag_measurements = (SinkBuffer.package_setter(anchor_0, tag) for _, tag in enumerate(tags))
            for tag_measurement in tag_measurements:
                if not self.__get_simulated_noise():
                    measurements.append(frame_builder(*tag_measurement))
            collection += measurements
        return collection

    def generate_buffer_tags_only(self, tags):
        collection = []
        for i, anchor_0 in enumerate(self.__anchors):
            measurements = []
            tag_measurements = (SinkBuffer.package_setter(anchor_0, tag) for _, tag in enumerate(tags))
            for tag_measurement in tag_measurements:
                if not self.__get_simulated_noise():
                    measurements.append(frame_builder(*tag_measurement))
            collection += measurements
        return collection

    def locate_in_bandwidth(self):
        draw_value = uniform(0, 1)
        bandwidth_value = None
        for i, value in enumerate(self.__ranges):
            if draw_value <= value:
                bandwidth_value = self.__bandwidths_length[i]
                break
        return bandwidth_value

    def __get_simulated_noise(self):
        if self.__noise == 0 or not self.__noise_allowed:
            return False
        lottery_number = randint(0, 100)
        if lottery_number <= self.__noise:
            return True
        return False
