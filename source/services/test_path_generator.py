# import unittest
# from path_generator import Path
# from numpy.testing import assert_allclose
#
#
# class TestPathProvider(unittest.TestCase):
#     def test_instance_of_returned_object(self):
#         anchors_coordination = [
#             {'id': 0, 'x': 0, 'y': 0},
#             {'id': 1, 'x': 0, 'y': 100},
#             {'id': 2, 'x': 100, 'y': 100},
#             {'id': 3, 'x': 100, 'y': 0}
#         ]
#         path_crossing_point_coordination = [{'x': 10, 'y': 10}, {'x': 10, 'y': 90}, {'x': 90, 'y': 90},
#                                             {'x': 90, 'y': 10}, {'x': 10, 'y': 10}]
#         self.assertIsInstance(Path(anchors_coordination, 10999)
#                               .line_walk(path_crossing_point_coordination), list,
#                               'returned object is an instance of list')
#
#     def test_instance_of_item_in_returned_list(self):
#         anchors_coordination = [{'id': 0, 'x': 0, 'y': 0}, {'id': 1, 'x': 0, 'y': 100}, {'id': 2, 'x': 100, 'y': 100},
#                                 {'id': 3, 'x': 100, 'y': 0}]
#         path_crossing_point_coordination = [{'x': 10, 'y': 10}, {'x': 10, 'y': 90}, {'x': 90, 'y': 90},
#                                             {'x': 90, 'y': 10}, {'x': 10, 'y': 10}]
#         self.assertIsInstance(
#             Path(anchors_coordination, 10999)
#                 .line_walk(path_crossing_point_coordination)[0], list, 'item in returned list is an instance of list')
#
#     def test_instance_of_item_in_distances_set(self):
#         anchors_coordination = [{'id': 0, 'x': 0, 'y': 0}, {'id': 1, 'x': 0, 'y': 100}, {'id': 2, 'x': 100, 'y': 100},
#                                 {'id': 3, 'x': 100, 'y': 0}]
#         path_crossing_point_coordination = [{'x': 10, 'y': 10}, {'x': 10, 'y': 90}, {'x': 90, 'y': 90},
#                                             {'x': 90, 'y': 10}, {'x': 10, 'y': 10}]
#         self.assertIsInstance(
#             Path(anchors_coordination, 10999)
#                 .line_walk(path_crossing_point_coordination)[0][0], dict,
#             'item in returned list of distances has item with instance of dict')
#
#     def test_instance_of_item_of_key_name_dist(self):
#         anchors_coordination = [{'id': 0, 'x': 0, 'y': 0}, {'id': 1, 'x': 0, 'y': 100}, {'id': 2, 'x': 100, 'y': 100},
#                                 {'id': 3, 'x': 100, 'y': 0}]
#         path_crossing_point_coordination = [{'x': 10, 'y': 10}, {'x': 10, 'y': 90}, {'x': 90, 'y': 90},
#                                             {'x': 90, 'y': 10}, {'x': 10, 'y': 10}]
#         self.assertIsInstance(
#             Path(anchors_coordination, 10999)
#                 .line_walk(path_crossing_point_coordination)[0][0]['dist'], int,
#             'item in first returned dict equals 0')
#
#     def test_distances_for_each_anchor_square_path(self):
#         anchors_coordination = [{'id': 0, 'x': 0, 'y': 0}, {'id': 1, 'x': 0, 'y': 100}, {'id': 2, 'x': 100, 'y': 100},
#                                 {'id': 3, 'x': 100, 'y': 0}]
#         path_crossing_point_coordination = [{'x': 10, 'y': 10}, {'x': 10, 'y': 90}, {'x': 90, 'y': 90},
#                                             {'x': 90, 'y': 10}, {'x': 10, 'y': 10}]
#
#         # we are creating array for 16 distances for created path as checking array
#         # distance = math.sqrt((ax - x)**2 + (ay - y)**2)
#         anchor_0_distances = [14, 32, 51, 71, 91, 100, 103, 118, 127, 118, 103, 100, 91, 71, 51, 32, 14]
#         anchor_1_distances = anchor_0_distances[4:len(anchor_0_distances) - 1] + anchor_0_distances[0:5]
#         anchor_2_distances = anchor_0_distances[8:len(anchor_0_distances) - 1] + anchor_0_distances[0:9]
#         anchor_3_distances = anchor_0_distances[12:len(anchor_0_distances) - 1] + anchor_0_distances[0:13]
#
#         frames = Path(anchors_coordination, 10999).line_walk(path_crossing_point_coordination)
#         frames_number = len(frames)
#         check_point_separation = int(round(frames_number / (len(anchor_0_distances) - 1), 0))
#         for index in range(len(anchor_0_distances) - 1):
#             desired_0 = anchor_0_distances[index]
#             actual_0 = frames[index * check_point_separation][0]['dist']
#             assert_allclose(desired_0, actual_0, 1)
#
#             desired_1 = anchor_1_distances[index]
#             actual_1 = frames[index * check_point_separation][3]['dist']
#             assert_allclose(desired_1, actual_1, 1)
#
#             desired_2 = anchor_2_distances[index]
#             actual_2 = frames[index * check_point_separation][2]['dist']
#             assert_allclose(desired_2, actual_2, 1)
#
#             desired_3 = anchor_3_distances[index]
#             actual_3 = frames[index * check_point_separation][1]['dist']
#             assert_allclose(desired_3, actual_3, 1)
#
#     def test_distances_for_each_anchor_slant_path(self):
#         anchors_coordination = [{'id': 0, 'x': 0, 'y': 0}, {'id': 1, 'x': 0, 'y': 100}, {'id': 2, 'x': 100, 'y': 100},
#                                 {'id': 3, 'x': 100, 'y': 0}]
#         path_crossing_point_coordination = [{'x': 10, 'y': 10}, {'x': 90, 'y': 90}, {'x': 10, 'y': 10}]
#
#         anchor_0_distances = [14, 42, 71, 99, 127, 98, 71, 42, 14]
#         anchor_1_distances = [91, 76, 71, 76, 91, 76, 71, 76, 91]
#         anchor_2_distances = anchor_0_distances[4:len(anchor_0_distances) - 1] + anchor_0_distances[0:5]
#         anchor_3_distances = anchor_1_distances
#
#         frames = Path(anchors_coordination, 10999).line_walk(path_crossing_point_coordination)
#         frames_number = len(frames)
#         check_point_separation = int(round(frames_number / (len(anchor_0_distances) - 1), 0))
#
#         for index in range(len(anchor_0_distances) - 1):
#             desired_0 = anchor_0_distances[index]
#             actual_0 = frames[index * check_point_separation][0]['dist']
#             assert_allclose(desired_0, actual_0, 1)
#
#             desired_1 = anchor_1_distances[index]
#             actual_1 = frames[index * check_point_separation][3]['dist']
#             assert_allclose(desired_1, actual_1, 1)
#
#             desired_2 = anchor_2_distances[index]
#             actual_2 = frames[index * check_point_separation][2]['dist']
#             assert_allclose(desired_2, actual_2, 1)
#
#             desired_3 = anchor_3_distances[index]
#             actual_3 = frames[index * check_point_separation][1]['dist']
#             assert_allclose(desired_3, actual_3, 1)
#
#
# if __name__ == '__main__':
#     unittest.main()
