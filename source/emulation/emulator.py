import asyncio
import sys
import time
import websockets
from threading import Thread
from source.services.sink_buffer_imitator import SinkBuffer
from source.services.console_printer import dashed_printer, star_enclosed_print, separation_printer
from source.utils.data_setter import get_devices_list_as_json, json_to_object
from source.settings.configurations import PAYLOAD_FILE_PATH
from source.settings.configurations import WRITE_PAYLOAD_FRAMES
from source.settings.configurations import WS_EMITTING_TIME_STEP_IN_SECONDS
from source.settings.configurations import GLOBAL_BUFFER_SIZE
from source.settings.configurations import NOISE
import json


class Emulator:
    """
    Emulator class sends json packages over web socket to specified endpoint.
    Json package is composed to imitate as close as possible IndoorNavi
    hardware json package that is send from sink to backend.
    This is core mechanism that allows to emulate hardware
    real behavior such as:
    Stress test by flooding backend with huge amount
    of measurements per package.
    Emulation of moving tag, by composing path and sending
    step by step tag on path measurements.
    """
    __ws = websockets
    # Emit package with dimensions every given number of second [s]
    __ws_emitting_time_step = WS_EMITTING_TIME_STEP_IN_SECONDS
    __global_buffer_size = GLOBAL_BUFFER_SIZE
    __emulator_can_be_run = True
    __info = []
    __errors = []
    __buffer_size = 8
    __workers = set()
    __active_tags = {}
    __used_tags = set()
    __tags_path_length = {}
    __tags_path = {}
    __tags_floor_sequence = {}
    __counters = {}
    __paths = []

    @staticmethod
    def set_anchors_location(data):
        anchor_coordinates = []
        anchors = data['anchors']
        for anchor in anchors:
            if isinstance(anchor['shortId'], int) and \
                    isinstance(anchor['x'], int) and \
                    isinstance(anchor['y'], int) and \
                    isinstance(anchor['z'], int):
                anchor_coordinates.append({
                    'id': anchor['shortId'],
                    'x': anchor['x'],
                    'y': anchor['y'],
                    'z': anchor['z']
                })
        return anchor_coordinates

    @staticmethod
    def __write_package_to_file(packages_to_write):
        """
        Writes data to file
        :param packages_to_write: data to write
        :return: void
        """
        try:
            with open(PAYLOAD_FILE_PATH, 'a+') as f:
                f.write(str(json.dumps(packages_to_write)))
                f.write('\n')
                dashed_printer('Writing payload with web socket frames in to a file: {}'
                               .format(PAYLOAD_FILE_PATH))
        except ValueError:
            print('File {} does not exist, data is not written'.format(
                PAYLOAD_FILE_PATH))
            # raise Exception('File {} does not exist, data is not written'.format(PAYLOAD_FILE_PATH))

    def __init__(self, tags, back_end_socket, number_of_sinks=1):
        """
        :param tags: tags object list to emulate
        :param back_end_socket: socket address
        :param number_of_sinks: number of sinks set on each floor #todo: in future should be set per worker
        """
        self.__number_of_sinks = number_of_sinks
        self.__ws_address = back_end_socket
        for tag in tags:
            if tag['closed']:
                points = list(tag['coordinates'])
                points.append(tag['coordinates'][0])
            else:
                reversed_points = list(tag['coordinates'])
                reversed_points.reverse()
                points = tag['coordinates'] + \
                    reversed_points[1:len(reversed_points)]
            tag_id = int(tag['tag_short_id'])
            emulation = {
                'points': points,
                'tag': tag_id,
                'floors': tag['floors']
            }
            self.__verify_data_provided(emulation)
            self.__tags_path_length[tag_id] = len(points)
            self.__tags_path[tag_id] = points
            self.__tags_floor_sequence[tag_id] = tag['floors']
            self.__counters[tag_id] = 0
            self.__paths.append(emulation)
            for floor_number in tag['floors']:
                self.__workers.add(floor_number)

    def __del__(self):
        del self.__ws_address

    def emit(self, emitting_time=0):
        """
        Separates emitting process and sets to workers.
        Each worker represents different floor number
        :param emitting_time: time for how long emitter will run
        :return: void
        """
        for worker in self.__workers:
            new_loop = asyncio.new_event_loop()
            session_tags = [p for p in self.__paths
                            if worker in p['floors']]
            thread_worker = Thread(
                target=self.__floor_emulator,
                args=(emitting_time, session_tags, worker, new_loop),
                name='worker_{}'.format(worker)
            )
            thread_worker.start()

    def __floor_emulator(self, emitting_time, session_tags, worker, loop):
        """
        Starts event loop
        Passes async socket emitter to this event loop
        :param emitting_time: time for how long emitter will run
        :param session_tags: all tags that can be emulated for given worker
        :param worker: worker unique number corresponding to floor number
        :param loop: event loop for async socket emitter
        :return: void
        """
        self.__set_active_tags(session_tags, worker)
        asyncio.set_event_loop(loop)
        loop.run_until_complete(
            self.__run_async_emitter(emitting_time, worker))

    def __set_active_tags(self, session_tags, worker):
        """
        Sets beginning schema of active tags for emulation
        :param session_tags: all tags that can be emulated for given worker
        :param worker: worker unique number corresponding to floor number
        :return: void
        """
        self.__active_tags[worker] = [i['tag'] for i in session_tags
                                      if i['tag'] not in self.__used_tags]
        for used_tag in self.__active_tags[worker]:
            self.__used_tags.add(used_tag)

    async def __run_async_emitter(self, emitting_time, worker):
        """
        Sets async connection with web socket per worker
        :param emitting_time: time for how long emitter will run
        :param worker: worker unique number corresponding to floor number
        :return: void
        """
        async with self.__ws.connect(self.__ws_address) as socket:
            time_to_stop = int(time.time() + emitting_time)
            infinity_loop = False
            if emitting_time == 0:
                infinity_loop = True
            response = await socket.recv()
            decoded = json_to_object(response)
            floor_indexes_to_del = []
            for anchor in decoded['anchors']:
                if anchor['floor'] and anchor['floor']['id'] != worker:
                    floor_indexes_to_del.append(
                        decoded['anchors'].index(anchor))
            for index in floor_indexes_to_del[::-1]:
                del decoded['anchors'][index]
            if len(decoded['anchors']) == 0:
                dashed_printer(
                    'There is no anchors available on given floor {}.'.format(worker))
            sink_buffer = SinkBuffer(Emulator.set_anchors_location(decoded))
            if type(NOISE) is int:
                sink_buffer.noise = NOISE
            elif type(NOISE) is tuple or type(NOISE) is list:
                sink_buffer.bandwidths = NOISE
            else:
                raise Exception('''
                    Wrong NOISE parameter passed in to emulator
                    configuration should be integer or array
                    ''')
            await self.__start_emitter_process(
                worker,
                socket,
                sink_buffer,
                time_to_stop,
                infinity_loop
            )
            return

    async def __start_emitter_process(
            self, worker,
            socket, sink_buffer,
            time_to_stop, infinity_loop
    ):
        """
        Async base emitter function
        :param worker: worker unique number
        :param socket: socket object for worker connection
        :param sink_buffer: sink buffer object dedicated to particular worker
        :param time_to_stop: time when worker should stop
        :param infinity_loop: flag, if True emitter will run forever, else will stop at time_to_stop
        :return: void
        """
        packages_to_write = []
        package_counter = 0
        while True:
            measurements = []
            tags = []
            for tag_id in self.__active_tags[worker]:
                counter = self.__counters[tag_id]
                if counter != self.__tags_path_length[tag_id] - 1:
                    tag = {
                        'id': tag_id,
                        'x': self.__tags_path[tag_id][counter]['x'],
                        'y': self.__tags_path[tag_id][counter]['y'],
                        'z': self.__tags_path[tag_id][counter]['z']
                    }
                    tags.append(tag)
                    self.__counters[tag_id] += 1
                else:
                    self.__counters[tag_id] = 0
                    self.__allocate_tag_to_next_worker(tag_id, worker)
                measurements = sink_buffer.generate_buffer_tags_only(tags)
            if len(sink_buffer.bandwidths) > 0:
                max_slice_value = sink_buffer.locate_in_bandwidth()
                socket_payload = measurements[:max_slice_value]
            else:
                socket_payload = measurements
            payload_length = len(socket_payload)
            payload_sink_divisor = int(payload_length / self.__number_of_sinks)
            payload_start_index = 0
            payload_finish_index = payload_sink_divisor
            for _ in range(self.__number_of_sinks):
                sink_payload = socket_payload[payload_start_index:payload_finish_index]
                if len(sink_payload) > self.__global_buffer_size:
                    sink_payload_length = len(sink_payload)
                    first_in_iteration = 0
                    last_in_iteration = self.__global_buffer_size
                    while True:
                        sink_payload_part = sink_payload[first_in_iteration:last_in_iteration]
                        first_in_iteration = last_in_iteration
                        star_enclosed_print(
                            'Number of measurements per one package (sink device) is {} distances'.format(len(sink_payload_part)))
                        package = get_devices_list_as_json(sink_payload_part)
                        # self.__print_measurements(sink_payload_part)
                        await socket.send(package)
                        if last_in_iteration == sink_payload_length:
                            break
                        if last_in_iteration + 100 < sink_payload_length:
                            last_in_iteration += 100
                        else:
                            last_in_iteration += sink_payload_length - last_in_iteration
                else:
                    package = get_devices_list_as_json(sink_payload)
                    # self.__print_measurements(sink_payload)
                    star_enclosed_print(
                        'Number of measurements per one package (sink device) is {} distances'.format(len(sink_payload)))
                    await socket.send(package)
                separation_printer(
                    'Floors with active tags {}'.format(self.__active_tags))
                star_enclosed_print('Frame separation: {} s'
                    .format(self.__ws_emitting_time_step / self.__number_of_sinks))
                payload_start_index += payload_sink_divisor
                payload_finish_index += payload_sink_divisor
                time.sleep(self.__ws_emitting_time_step /
                           self.__number_of_sinks)
                if WRITE_PAYLOAD_FRAMES:
                    payload_size = sys.getsizeof(package)
                    packages_to_write.append({
                        "time": time.time(),
                        "frame": package,
                        "frame_size_in_bytes": payload_size,
                        "frame_time_separation": self.__ws_emitting_time_step / self.__number_of_sinks
                    })
                    if package_counter > self.__global_buffer_size:
                        Emulator.__write_package_to_file(packages_to_write)
                        del packages_to_write[:]
                        package_counter = 0
                    package_counter += 1
            time_after = time.time()
            seconds_left = int(time_to_stop - time_after)
            if seconds_left > 1:
                dashed_printer("""
                This stress test will last for {} seconds
                """.format(seconds_left))
            if not infinity_loop and seconds_left < 1:
                Emulator.__write_package_to_file(packages_to_write)
                dashed_printer('Emulation has been finished')
                break

    def __verify_data_provided(self, emulation):
        """
        Verifies if given data are correct
        :param emulation: data to verify
        :return: void
        """
        if not isinstance(emulation['points'], list) and len(emulation['points']) < 2:
            self.__emulator_can_be_run = False
            self.__errors.append('coordinates')
        if not isinstance(emulation['tag'], int) and \
                (emulation['tag'] < 1 or emulation['tag'] > 99999):
            self.__emulator_can_be_run = False
            self.__errors.append('tag number')
        if self.__emulator_can_be_run is False:
            raise Exception(
                'Data provided are incorrect, please set correct parameters for {}'
                .format(', '.join(self.__errors)))

    def __allocate_tag_to_next_worker(self, tag_id, previous_worker):
        i = self.__tags_floor_sequence[tag_id].index(previous_worker)
        if i == len(self.__tags_floor_sequence[tag_id]) - 1:
            next_worker = self.__tags_floor_sequence[tag_id][0]
        else:
            next_worker = self.__tags_floor_sequence[tag_id][i + 1]
        self.__active_tags[previous_worker].remove(tag_id)
        self.__active_tags[next_worker].append(tag_id)

    def __print_measurements(self, sink_payload):
        for measurement in sink_payload:
            print('t: ', measurement['did1'], ' a: ',\
                measurement['did2'], ' dist : ', measurement['dist'])


class StressEmulator(Emulator):
    """
    Emulates stress sending lots of meaningless data to check how backend will respond
    """

    def __init__(self, tags, back_end_socket, sinks):
        super().__init__(tags, back_end_socket, sinks)

    def __del__(self):
        super().__del__()

    def emit_stress(self, emitting_time):
        self.emit(emitting_time)

