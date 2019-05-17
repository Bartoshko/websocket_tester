import sys
from source.stress.structure_generator import StructureGenerator
from source.emulation.emulator import Emulator
from source.emulation.emulator import StressEmulator
from source.services.database_connector import DataBaseConnector
from source.services.console_printer import dashed_printer
from source.settings.configurations import BACK_END_SOCKET_ADDRESS, DEVICES_CONFIGURATION, PATH_CHECKPOINTS_NUMBER
from source.settings.configurations import DB_CONFIGURATION, WS_EMITTING_TIME_STEP_IN_SECONDS, DB_HASH_FILE_PATH
from source.utils.data_setter import get_settings
from source.services.path_generator import generate_path


def start_emulation(config_file_path):
    """start emulating path with configs form configuration json file"""
    tags = []
    for path_item in config_file_path:
        path_configuration = get_settings(path_item)
        speed = path_configuration['path']['parameters']['speed']
        path_closed = path_configuration['path']['parameters']['closed']
        coordinates_configs = path_configuration['path']['coordinates']
        floor_numbers = path_configuration['floors']
        coordinates = generate_path(
            coordinates_configs,
            speed, WS_EMITTING_TIME_STEP_IN_SECONDS)
        tag = {
            'closed': path_closed,
            'coordinates': coordinates,
            'tag_short_id': path_configuration['tag_short_id'],
            'floors': floor_numbers
        }
        tags.append(tag)
    number_of_tags_in_emulation = len(config_file_path)
    tags_verb_form = 'TAGS' if number_of_tags_in_emulation > 1 else 'TAG'
    dashed_printer('STARTING EMULATION FOR {} {}'.format(
        number_of_tags_in_emulation,
        tags_verb_form))
    emulator = Emulator(tags, BACK_END_SOCKET_ADDRESS)
    emulator.emit()
    del emulator


def start_stress_test(configuration):
    time_input_from_user = input('Specify for how long stress test should run \
                            in seconds, \
                            than press ENTER \
                            If not specified test will run 100 seconds: ')
    floor_input_from_user = input('Specify floor number to run test for \
                            than press ENTER \
                            If not specified test will run on floor 100: ')
    if time_input_from_user:
        time_input_from_user = int(time_input_from_user)
    else:
        time_input_from_user = 100
    if floor_input_from_user:
        floor_input_from_user = int(floor_input_from_user)
    else:
        time_input_from_user = 100
    structure_generator = StructureGenerator(
        floor_input_from_user,
        configuration['sinks'],
        configuration['anchors'],
        configuration['tags'])
    dashed_printer('Created stress strategy')
    tags_id = structure_generator.insert_structure_to_database()
    tags_to_emulate = []
    dashed_printer('Database has been backed up')
    dashed_printer('Inserted stress data to database')
    input('PRESS ENTER TO CONTINUE')
    for tag_id in tags_id:
        coordinates = []
        for random_coordinates in range(PATH_CHECKPOINTS_NUMBER):
            random_coordinates = structure_generator.generate_random_coordinates_range()
            coordinates.append({
                'x': random_coordinates[0],
                'y': random_coordinates[1],
                'z': random_coordinates[2]
            })
        tag = {
            'closed': False,
            'coordinates': coordinates,
            'floors': [floor_input_from_user],
            'tag_short_id': tag_id
        }
        tags_to_emulate.append(tag)
    stress_emulator = StressEmulator(
        tags_to_emulate,
        BACK_END_SOCKET_ADDRESS, configuration['sinks'])
    stress_emulator.emit_stress(time_input_from_user)
    del stress_emulator
    input('PRESS ENTER TO CONTINUE')
    dashed_printer('Waiting to rollback database from backup')
    structure_generator.clean_after_test()
    del structure_generator
    dashed_printer('Data base has been rolled back to last back up')
    dashed_printer('--- STRESS TEST FINISHED ---')


def evaluate_parameters():
    if len(sys.argv) == 1:
        raise Exception('After calling python script specify valid command'
                        'that needs to be executed, '
                        'for emulating write "path",'
                        'for testing backend write "stress", '
                        'for creating new database hash write "dbhash"')
    if sys.argv[1] == 'stress':
        if len(sys.argv) == 5:
            args_provided = sys.argv[2: len(sys.argv)]
            DEVICES_CONFIGURATION['sinks'] = int(args_provided[0])
            DEVICES_CONFIGURATION['anchors'] = int(args_provided[1])
            DEVICES_CONFIGURATION['tags'] = int(args_provided[2])
            start_stress_test(DEVICES_CONFIGURATION)
        else:
            a = DEVICES_CONFIGURATION['sinks']
            b = DEVICES_CONFIGURATION['sinks'] * \
                DEVICES_CONFIGURATION['anchors']
            c = DEVICES_CONFIGURATION['tags']
            print('Emulator will use default configuration for stress testing,' +
                  ' total number of sinks {0}, anchors {1}, tags {2}'
                  .format(a, b, c))
            start_stress_test(DEVICES_CONFIGURATION)
    elif sys.argv[1] == 'path':
        config_file_paths = []
        if len(sys.argv) > 2:
            args_provided = sys.argv[2: len(sys.argv)]
            for arg in args_provided:
                try:
                    config_file_paths.append(arg)
                except ValueError:
                    raise ValueError
            start_emulation(config_file_paths)
        else:
            try:
                config_file_paths.append('paths/default.json')
                print('Emulator will use default configuration for path \
                emulation from paths/default.json')
            except ValueError:
                raise ValueError
            start_emulation(config_file_paths)
    elif sys.argv[1] == 'dbhash':
        stress = DataBaseConnector(DB_CONFIGURATION)
        stress.create_fresh_db_hash(DB_HASH_FILE_PATH)
        del stress
    elif sys.argv[1] == 'generate':
        config_file_paths = []
        args_provided = [sys.argv[2] for _ in range(0, int(sys.argv[3]))]
        for arg in args_provided:
            try:
                config_file_paths.append(arg)
                # todo: increase tag id for each added arg path i += 1 and add to db
            except ValueError:
                raise ValueError
        start_emulation(config_file_paths)


if __name__ == '__main__':
    evaluate_parameters()
