# Emulator Indoor - Navi

Emulates the behavior of hardware, in this case sink emitter. Imitates distances between tag and all anchors that are installed for test.

## Installing

### Please use python 3.5 or greater

Open terminal and go to Your project main catalogue.

1. Install virtualenv:
```bash
$ pip3 install virtualenv
```

2. Test Your virtual environment:
```bash
$ virtualenv --version
```

3. Create local environment:

```bash
$ cd my_project_folder or ve
```
```bash
$  virtualenv my_project or virtualenv ve
```

4. Run local environment:
```bash
$ source ./ve/bin/activate
```

5. Install packages

Install global in your system
```bash
$ pip install psutil
```
Install in virtual environment
```bash
$ pip3 install -r requirements.txt
```

6. For visualization 

$ apt install matplotlib

$ apt install python3-tk

## Configuration file

### In file ```settings/configurations.py```

1. Global variable ```DEVICES_CONFIGURATION```
holds data for stress test when test is run from docker container. To change stress test
settings, please put desired numbers of sinks, anchors and tags.

2. Global variable ```DB_CONFIGURATION```
holds information for database configuration.

3. Global variable ```FLOOR_NUMBER_FOR_TEST```
holds information on which floor test will be performed

4. Global variable ```BACK_END_SOCKET_ADDRESS```
holds address to backend web socket.

5. Global variable ```DB_HASH_FILE_PATH```
holds path to file where database hash is stored
  
  
## Running the tests

Run:

- Check if data are set correctly:

$ python3 test_DataSetter.py

-  Check if path provides proper data instance:

$python3 test_PathProvider.py

## Set and run docker image for stress test

```bash
$ chmod +x run.sh
```
then:
```bash
$ run.sh
```

## Emulators modules

1. Emulation server which sends emulated packets over web socket to backend server.

2. Plotter which plots graphic representation of given path 


# Run Emulator:

1. path is given:
```
$ python3 start.py path <paths to config file *.json>
```
2. path is not given will work with default settings:
```
$ python3 start.py path
```
3. randomize frames for tests performance

```
$ python3 start.py stress 'Sinks' 'Anchors' 'Tags'
```

- Sinks - number of sinks - socket connections created per test

- Anchors - number of anchors per sink

- Tags - number of tags 
 
With stress test command emulator is going to wait for the message from the logger
and than starts emitting specified stress test scenario. So there is necessity to run
emulator before running logger.

4. set fresh database hash

```
$ python3 start.py dbhash
```

When database architecture changes then exception for unit test 
and docker image build will be raised.
This is caused when there is inconsistency between Emulator model of database
and real database structure. While running performance tests using Emulator,
User needs to be sure that database model is consistent with real database structure,
to have possibility to handle exceptions.

Run this command to update your db model in Emulator 

5. View path plot
```
$ python3 ploter.py <path to config file *.json>
```

6. View and plot system load from given performance_log_file:

```
$ python3 system_load.py <path to performance log file *.txt>
```

and fallow the bash instructions.

## Getting Started with Emulation server

Emulator connects with back - end server over web socket, for emulating behavior while hosting server locally this is the web socket address: "ws://localhost:90/measures?server"

### Configuration

#### Path JSON
Emulator gets configuration from file ./data/path.json - this file is required to set first before starting Emulator - Indoor Navi
As described bellow:

Given example:

```
{
    "path": {
        "coordinates": [
            {"x": 0, "y": 0},
            {"x": 300, "y": 150},
            {"x": 300, "y": 500},
            {"x": 1000, "y": 1000},
            {"x": 50, "y": 50}
        ],
        "parameters": {
            "speed": 100,
            "curved": false,
            "closed": false
        }
    },
    "tag_short_id": 10999
}
```

##### Explanation:

- path - contains all necessary information for simulating tag movement
- coordinates - contains list of crossing point coordinates of x and y for path to be drawn
- x and y - are in [cm] measured from [0,0] and both are non zero integers
- parameters - specifies how path will be walked by tag
- speed - number representing speed in [cm / s]
- loss - number representing probability of loosing frames where 0 is all frames will be sent 100 all will be lost
- curved - boolean representing interpolation method: False - line interpolation, True - polynomial interpolation
- closed - boolean representing type of path that will be walked,
        True means that path is closed by walking from last cross point to the beginning by interpolating path from this two points,
        False means that path is walked back (reversed for going back to starting point)
- STARTING POINT is the first declared point in coordinates -> coordinates[0]
- tag_short_id - is a preset id number of tag that distances to will be emitted

#### Configuration of server connection, database, hardware parameters

All parameters are set in:
```source/settings/configuration.py ```

Files looks like this:

```
DB_CONFIGURATION = {
    'user': 'root',
    'password': '',
    'host': '172.16.170.60',
    'database': 'Navi'
}

DEVICES_CONFIGURATION = {
    'sinks': 5,
    'anchors': 8,
    'tags': 40
}
 
PROBE_TIME = 100

FLOOR_NUMBER_FOR_TEST = 100

# BACK_END_SOCKET_ADDRESS = "ws://172.16.170.20:90/measures?emulator"
BACK_END_SOCKET_ADDRESS = "ws://172.16.170.60:90/measures?emulator"

DB_HASH_FILE_PATH = "source/settings/db_hash.json"

PAYLOAD_MEASUREMENT_SERVER_ADDRESS = '0.0.0.0'
PAYLOAD_MEASUREMENT_SERVER_PORT = 8080
WRITE_PAYLOAD_FRAMES = True
PAYLOAD_FILE_PATH = "measurements/payloads.txt"

# HARDWARE PARAMETERS, time in seconds
WS_EMITTING_TIME_STEP = 2
SINGLE_MEASURE_SEPARATION_TIME_STEP = 0.015
SINK_BUFFER_RELEASE_TIME_STEP = 0.5
GLOBAL_BUFFER_SIZE = 100
NOISE = 8
# NOISE = ((27, 111), (26, 102), (28, 84), (25, 72), (29, 35), (23, 9), (22, 4), (21, 2))
```

##### Description

- DB_CONFIGURATION - database adress and parameters served by back-end that emulator with connect to.
- DEVICES_CONFIGURATION - default device arrangement that will be emulated if no parameters will be passed
when starting emulator with ```stress``` parameter
- PROBE_TIME - default time span for emulator to emulate packages if no time will be specified when starting emulator
with ```stress``` parameter
- FLOOR_NUMBER_FOR_TEST - floor on which emulator will set emulation strategy in database and on witch emulation will occur 
- BACK_END_SOCKET_ADDRESS - websocket address to which emulator will send emulated payload packages
- DB_HASH_FILE_PATH - path to file where database hash is stored
- PAYLOAD_MEASUREMENT_SERVER_ADDRESS - emulator server is served from this ip to collect measurements
from hardware real packages, ```0.0.0.0``` means that server is visible from outside localhost
- PAYLOAD_MEASUREMENT_SERVER_PORT - port on which server is collecting payloads
- WRITE_PAYLOAD_FRAMES - if set as true than server will write collected payload packages to a file
- PAYLOAD_FILE_PATH - path to a file where payload is going to be written
- WS_EMITTING_TIME_STEP - time step of device hosting sink according to which payload is send to the back-end
server

- GLOBAL_BUFFER_SIZE - sink measurements buffer size
- NOISE - percentage of noise probability that can be applied to each measurements given as integer from 0 to 100. 
Or when given as array of two dimensional arrays of probabilities distribution, then index zero reflects number of 
measurements in frame and index one reflects its possibility of this frame length to occur
in regard to sum of all specified probabilities. 
This allows to record hardware frame length (measurements in frame) over specified time
and use exact distribution as desired probability distribution in future emulation. 
 

#### System Load Collection

WORKS ONLY ON LINUX ENVIRONMENT or IN DOCKER CONTAINER WITH LINUX KERNEL

To collect system in csv format run ```$ chmod +x collect_system_load/top_to_output.sh```, than run ```collect_system_load/top_to_output.sh```

Session load will be collected in  ```collect_system_load/out.txt```

#### System Load Analyses

To analyze system load run in terminal:
```
$ python3 system_load.py <path_to_collected_load_file.txt>
```
 
## Version
 
This is version 0.0.1

## Authors

Bartosz Lenart

## License

MIT

## Acknowledgments

