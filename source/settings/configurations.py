DB_CONFIGURATION = {
    'user': 'root',
    'password': 'password',
    'host': 'core:8080',
    'database': 'Navi'
}

DEVICES_CONFIGURATION = {
    'sinks': 5,
    'anchors': 8,
    'tags': 40
}

PATH_CHECKPOINTS_NUMBER = 600

FLOOR_NUMBER_FOR_TEST = 3

# change DB_CONFIGURATION host when changing BACK_END_SOCKET_ADDRESS
# BACK_END_SOCKET_ADDRESS = "ws://172.16.170.47:90/measures?emulator"
# BACK_END_SOCKET_ADDRESS = "ws://localhost:90/measures?emulator"
# BACK_END_SOCKET_ADDRESS = "ws://core:8080/measures?emulator"
BACK_END_SOCKET_ADDRESS = "ws://192.168.1.10:3001"

DB_HASH_FILE_PATH = "source/settings/db_hash.json"

PAYLOAD_MEASUREMENT_SERVER_ADDRESS = '0.0.0.0'
PAYLOAD_MEASUREMENT_SERVER_PORT = 8080
WRITE_PAYLOAD_FRAMES = False
PAYLOAD_FILE_PATH = "measurements/payloads_backend_test.txt"

WS_EMITTING_TIME_STEP_IN_SECONDS = .1
GLOBAL_BUFFER_SIZE = 100
NOISE = 0
# NOISE = ((27, 111), (26, 102), (28, 84), (25, 72), (29, 35), (23, 9), (22, 4), (21, 2))
