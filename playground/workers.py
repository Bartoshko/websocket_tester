from threading import Thread
from time import sleep
from random import uniform
from random import randint

"""
This module is written as less complicated example how multi threading process
has been designed for Emulator purpose and deliberately async code has not been
included in example. All this would help to understand how emulator multi thread works.
Please do not remove this module as this will help for future development
and understand multi threading process implementation.
If anything regarding to multi threading will be changed,
added or removed in emulator.py module, please do consider it in this example.
"""

# create fake emulation for test
emulations_fake = [
    {
        'floors': [z for z in range(randint(1, 10))],
        'path': {
            'tag': i,
            'coordinates': [
                {'x': a * i, 'y': a * i} for a in range(randint(5, 25))
            ]
        }
    }
    for i in range(1, 10)
]


class WorkersController:
    """
    This is simplified implementation of Emulator multi threading process
    """
    __workers = set()
    __active_tags = {}
    __paths = []
    __used_tags = set()
    __tags_path_node = {}
    __tags_path_length = {}
    __tags_path = {}
    __tags_floor_sequence = {}

    def __init__(self, emulations):
        for emulation in emulations:
            for floor_number in emulation['floors']:
                self.__workers.add(floor_number)
            self.__paths.append(emulation)
            self.__tags_path_node[emulation['path']['tag']] = \
                len(emulation['path']['coordinates']) - 1
            self.__tags_path_length[emulation['path']['tag']] = \
                len(emulation['path']['coordinates'])
            self.__tags_path[emulation['path']['tag']] = \
                emulation['path']['coordinates']
            self.__tags_floor_sequence[emulation['path']['tag']] = \
                emulation['floors']

    def emulate(self):
        """
        Set workers for each emulation
        :return: void
        """
        for worker in self.__workers:
            session_tags = [p for p in self.__paths if
                            worker in p['floors']]
            threaded_worker = Thread(
                target=self.__emulator,
                args=(session_tags, worker),
                name='worker_{}'.format(worker)
            )
            threaded_worker.start()

    def __emulator(self, session_tags, worker):
        """
        Emulate tags movement for all tags in given session
        :param session_tags: list of tags that are possible for emulation
        :param worker: worker unique number
        :return: void
        """
        path_steps = 100
        self.__active_tags[worker] = \
            [tag['path']['tag'] for tag in session_tags
             if tag['path']['tag'] not in self.__used_tags]
        for used_tag in self.__active_tags[worker]:
            self.__used_tags.add(used_tag)
        while path_steps > 0:
            path_steps -= 1
            for tag in self.__active_tags[worker]:
                node = self.__tags_path_node[tag]
                # coordinates = self.__tags_path[tag][node]
                # print('worker {}, tag: {}, coordinates: {}'
                #       .format(worker, tag, coordinates))
                if node is not 0:
                    self.__tags_path_node[tag] -= 1
                else:
                    self.__tags_path_node[tag] = \
                        self.__tags_path_length[tag] - 1
                    self.__allocate_tag_to_next_worker(tag, worker)
            if len(self.__active_tags[worker]) > 0:
                print('WORKER {} TAGS: {}'
                      .format(worker, self.__active_tags[worker]))
            nap_t = uniform(1.2, 1.9)  # napping for random time
            sleep(nap_t)

    def __allocate_tag_to_next_worker(self, tag, previous_worker):
        """
        Reallocates tag to next session
        :param tag: tag unique id number
        :param previous_worker: previous worker unique number
        :return: void
        """
        i = self.__tags_floor_sequence[tag].index(previous_worker)
        if i == len(self.__tags_floor_sequence[tag]) - 1:
            worker = self.__tags_floor_sequence[tag][0]
        else:
            worker = self.__tags_floor_sequence[tag][i + 1]
        self.__active_tags[previous_worker].remove(tag)
        self.__active_tags[worker].append(tag)


if __name__ == '__main__':
    workers_controller = WorkersController(emulations_fake)
    workers_controller.emulate()
