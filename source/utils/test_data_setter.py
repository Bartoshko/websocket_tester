# runs tests
import unittest
from .data_setter import get_devices_list_as_json


fake_data_to_test = [{'signal': -60.02, 'did1': 10001, 'dist': 0, 'did2': 32001, 'fpa': -76.01, 'time': 0.0},
                     {'signal': -60.02, 'did1': 10001, 'did3': 32002, 'dist': 100, 'fpa': -76.01, 'time': 0.0},
                     {'signal': -60.02, 'did1': 10001, 'did4': 32003, 'dist': 100, 'fpa': -76.01, 'time': 0.0}]


class TestDataSetter(unittest.TestCase):
    def test_objectCreation_firs_member(self):
        self.assertIsInstance(get_devices_list_as_json(fake_data_to_test), str)


if __name__ == '__main__':
    unittest.main()
