import unittest

from teamcity import is_running_under_teamcity
from teamcity.unittestpy import TeamcityTestRunner

from source.services.database_connector import DataBaseConnector
from .structure_generator import StructureGenerator
from ..settings.configurations import DB_CONFIGURATION
from ..settings.configurations import DB_HASH_FILE_PATH
from ..settings.configurations import FLOOR_NUMBER_FOR_TEST


class TestDataBaseConnector(unittest.TestCase):
    def setUp(self):
        self.__log_inconsistant_hash = """
            Emulator database structure inconsistency with
            backend database structure.
            Update emulator database model.
            """
        # when
        self.__database = DataBaseConnector(DB_CONFIGURATION)

    def test_db_configuration_hash(self):
        # given
        actual_hash_configurations = self.__database.get_db_configuration()
        base_hash_configurations = DataBaseConnector.read_from_db_hash_file(DB_HASH_FILE_PATH)
        # then
        # test by assertion
        for actual, base in zip(actual_hash_configurations, base_hash_configurations):
            self.assertDictEqual(actual, base, self.__log_inconsistant_hash)


class TestStressGenerator(unittest.TestCase):
    maxDiff = None

    def setUp(self):
        # when
        self.stress_case = StructureGenerator(FLOOR_NUMBER_FOR_TEST, 1000, 10, 10)
        self.database = DataBaseConnector(DB_CONFIGURATION)

    def test_short_id_setting_is_always_unique(self):
        sinks_number = 7
        anchors_per_sink = 10
        tags_number = 45
        array_of_unique_ids = []
        for sink_id in StructureGenerator.generate_sinks_unique_id(sinks_number, anchors_per_sink):
            array_of_unique_ids.append(sink_id)
            for anchor_id in StructureGenerator.generate_anchor_unique_id(sink_id, anchors_per_sink):
                array_of_unique_ids.append(anchor_id)
        for tag_id in StructureGenerator.generate_tags_unique_id(tags_number):
            array_of_unique_ids.append(tag_id)
        self.assertEqual(len(array_of_unique_ids), len(set(array_of_unique_ids)))

    def test_device_random_coordinates_are_in_expected_range(self):
        # given
        for x in range(100):
            # than
            coordinates = StructureGenerator.generate_random_coordinates_range()
            self.assertLess(coordinates[0], 5001)
            self.assertLess(coordinates[1], 5001)

    def test_if_database_is_set_and_cleaned(self):
        # given
        sinks, anchors, tags = 10, 10, 10
        self.stress_case = StructureGenerator(FLOOR_NUMBER_FOR_TEST, sinks, anchors, tags)
        self.database.back_up_db()
        self.database.set_floor_for_test(100)
        self.database.delete_all_records_from_tables(('tag', 'sink', 'anchor', 'device'))
        unique_ids = []
        for unique_id in self.stress_case.generate_tags_unique_id(10):
            unique_ids.append(unique_id)
            self.database.start_new_db_connection()
            tag_long_id = StructureGenerator.generate_long_id(unique_id)
            self.database.insert_to_db(
                'device',
                ('shortId', 'longId', 'floor_id', 'verified'),
                (unique_id, tag_long_id, 100, True))
            db_tag_id = self.database.get_device_id(unique_id)
            self.database.insert_to_db('tag', ('id',), db_tag_id)
            db_id = self.database.get_device_id(unique_id)
            self.assertIsNotNone(db_id)
            self.assertEqual(db_id[0], unique_id)
            self.database.commit_to_db_and_close_connection()
        self.stress_case.clean_after_test()
        for unique_id in unique_ids:
            self.database.start_new_db_connection()
            db_id = self.database.get_device_id(unique_id)
            self.assertIsNone(db_id)
            self.database.commit_to_db_and_close_connection()



if __name__ == '__main__':
    if is_running_under_teamcity():
        runner = TeamcityTestRunner()
    else:
        runner = unittest.TextTestRunner()
    unittest.main(testRunner=runner)
