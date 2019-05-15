import asyncio
import websockets
import json
import pprint
from source.services.print_to_console import dashed_printer
from time import time
from source.settings.configurations import PAYLOAD_FILE_PATH, PAYLOAD_MEASUREMENT_SERVER_PORT, \
    PAYLOAD_MEASUREMENT_SERVER_ADDRESS

counter = 0
packages_to_write = []
time_length_of_probe = 60
time_to_finish = 0
socked_connected = False
time_0 = None


async def handler(websocket, _):
    global counter
    global packages_to_write
    global time_0
    global time_length_of_probe
    global socked_connected
    global time_to_finish
    if not socked_connected:
        time_0 = time()
        time_to_finish = int(time_0) + time_length_of_probe
        socked_connected = True
    time_counter = time()
    if time_counter < time_to_finish:
        with open(PAYLOAD_FILE_PATH, 'a') as f:
            payload = await websocket.recv()
            time_1 = time()
            if payload:
                counter += 1
                data_package = json.loads(payload)
                frame_time_separation = time_1 - time_0
                time_0 = time_1
                dashed_printer('Payload frame number {}'.format(counter))
                dashed_printer(' Received package format:')
                pprint.pprint(data_package)
                print('Package time separation is: {}'.format(frame_time_separation))
                dashed_printer(' -- -- -- end of payload frame -- -- --')
                packages_to_write.append({
                    "time": time(),
                    "frame": payload,
                    "frame_time_separation": frame_time_separation
                })
                if counter % 30 == 0:
                    dashed_printer('Writing to a file')
                    f.write(str(json.dumps(packages_to_write)))
                    f.write('\n')
                    del packages_to_write[:]
    else:
        if len(packages_to_write) > 0:
            with open(PAYLOAD_FILE_PATH, 'a') as f:
                dashed_printer('Writing to a file')
                f.write(str(json.dumps(packages_to_write)))
                f.write('\n')
                del packages_to_write[:]
            dashed_printer('PROBE TIME IS REACHED, WRITING TO A FILE IS STOPPED, YOU CAN STOP THE SERVER WITH ctrl + c')


if __name__ == '__main__':
    time_length_of_probe = int(input('Specify time span of this probe: '))
    asyncio.get_event_loop().run_until_complete(
        websockets.serve(handler, PAYLOAD_MEASUREMENT_SERVER_ADDRESS, PAYLOAD_MEASUREMENT_SERVER_PORT))
    asyncio.get_event_loop().run_forever()
