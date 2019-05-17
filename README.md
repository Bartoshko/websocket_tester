# Emulator

Emulates the behavior of hardware.

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

4. set fresh database hash

```
$ python3 start.py dbhash
```

5. View path plot
```
$ python3 ploter.py <path to config file *.json>
```

6. View and plot system load from given performance_log_file:

```
$ python3 system_load.py <path to performance log file *.txt>
```

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
 
## Version
 
This is version 0.0.1

## Authors

Bartosz Lenart

## License

MIT

## Acknowledgments

