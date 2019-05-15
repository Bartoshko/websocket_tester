from random import randint

from source.services.database_connector import DataBaseConnector
from ..settings.configurations import DB_CONFIGURATION
from ..settings.configurations import DB_HASH_FILE_PATH


class StructureGenerator:
    """
    StressGenerator class is responsible for generating stress strategy
    for testing backend.
    Generates stress load.
    Builds simplistic paths for tags movement.
    """

    short_max_value = 32767

    @staticmethod
    def generate_long_id(number):
        return int('{}{}'.format(number, number))

    @staticmethod
    def generate_short_id(number, device_type_code):
        return int('{}{}'.format(number, device_type_code))

    @staticmethod
    def generate_sinks_unique_id(sinks_number, anchors_per_sink):
        return (x * (anchors_per_sink + 1) for x in range(StructureGenerator.short_max_value + 1,
                                                          sinks_number + StructureGenerator.short_max_value + 1))

    @staticmethod
    def generate_anchor_unique_id(last_sink_id, anchors_per_sink):
        return (x for x in range(last_sink_id + 1, last_sink_id + anchors_per_sink + 1))

    @staticmethod
    def generate_tags_unique_id(tags_number):
        starting_tag_id = 1
        max_tag_id = starting_tag_id + tags_number
        if max_tag_id < StructureGenerator.short_max_value:
            return (x for x in range(starting_tag_id, max_tag_id))

    @staticmethod
    def generate_random_coordinates_range():
        return randint(0, 5000), randint(0, 5000), randint(0, 2000)

    def __init__(self, floor, sinks, anchors, tags):
        self.__floor = floor
        self.__sinks_number = sinks
        self.__anchors_number = anchors
        self.__tags_number = tags
        self.__database_connector = DataBaseConnector(DB_CONFIGURATION)

    def __del__(self):
        del self.__floor
        del self.__sinks_number
        del self.__anchors_number
        del self.__tags_number
        del self.__database_connector

    def insert_structure_to_database(self):
        self.__check_db_hash()
        self.__database_connector.back_up_db()
        self.__database_connector.set_floor_for_test(self.__floor)
        self.__database_connector.delete_all_records_from_tables(('tag', 'sink', 'anchor', 'device'))
        return self.__add_to_database()

    def clean_after_test(self):
        self.__database_connector.reload_from_db_back_up()

    def __check_db_hash(self):
        actual_hash_configurations = self.__database_connector.get_db_configuration()
        base_hash_configurations = DataBaseConnector.read_from_db_hash_file(DB_HASH_FILE_PATH)
        for actual, base in zip(actual_hash_configurations, base_hash_configurations):
            assert(actual == base)

    def __add_to_database(self):
        anchors_starting_id_index_per_sink = 0
        tags_starting_id_index_per_sink = 0
        tags = []
        self.__database_connector.start_new_db_connection()
        for sink_id in self.generate_sinks_unique_id(self.__sinks_number, self.__anchors_number):
            db_sink_id = self.__insert_sinks(sink_id)
            for anchor_id in StructureGenerator.generate_anchor_unique_id(
                    sink_id, self.__anchors_number):
                self.__insert_anchors(anchor_id, db_sink_id)
                anchors_starting_id_index_per_sink += self.__anchors_number
        for tag_id in StructureGenerator.generate_tags_unique_id(self.__tags_number):
            tags.append(tag_id)
            self.__insert_tags(tag_id)
            tags_starting_id_index_per_sink += self.__tags_number
        self.__database_connector.commit_to_db_and_close_connection()
        return tuple(tags)

    def __insert_sinks(self, sink_id):
        coordinates_sink = StructureGenerator.generate_random_coordinates_range()
        sink_long_id = StructureGenerator.generate_long_id(sink_id)
        self.__database_connector.insert_to_db(
            'device',
            ('shortId', 'longId', 'floor_id', 'verified'),
            (sink_id, sink_long_id, self.__floor, True))
        db_sink_id = self.__database_connector.get_device_id(sink_id)
        if db_sink_id is None:
            raise ValueError('sink is not set in devices')
        self.__database_connector.insert_to_db('anchor', ('id', 'x', 'y', 'z'), (
                db_sink_id + coordinates_sink))
        self.__database_connector.insert_to_db('sink', ('id', 'configured'), (db_sink_id[0], True))
        return db_sink_id

    def __insert_anchors(self, anchor_id, db_sink_id):
        coordinates_anchor = StructureGenerator.generate_random_coordinates_range()
        anchor_long_id = StructureGenerator.generate_long_id(anchor_id)
        self.__database_connector.insert_to_db(
            'device',
            ('shortId', 'longId', 'floor_id', 'verified'),
            (anchor_id, anchor_long_id, self.__floor, True))
        db_anchor_id = self.__database_connector.get_device_id(anchor_id)
        if db_anchor_id is None:
            raise ValueError('anchor is not set in devices')
        self.__database_connector.insert_to_db('anchor', ('id', 'x', 'y', 'z', 'sink_id'), (
            db_anchor_id + coordinates_anchor + db_sink_id))

    def __insert_tags(self, tag_id):
        tag_long_id = StructureGenerator.generate_long_id(tag_id)
        self.__database_connector.insert_to_db(
            'device',
            ('shortId', 'longId', 'floor_id', 'verified'),
            (tag_id, tag_long_id, self.__floor, True))
        db_tag_id = self.__database_connector.get_device_id(tag_id)
        if db_tag_id is None:
            raise ValueError('tag is not set in devices')
        self.__database_connector.insert_to_db('tag', ('id',), db_tag_id)
