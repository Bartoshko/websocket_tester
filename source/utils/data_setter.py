import json


def json_to_object(res_json):
    return json.loads(res_json)


def get_settings(path_to_file):
    with open(path_to_file) as json_parameters_for_payload_setting:
        return json.load(json_parameters_for_payload_setting)


def get_devices_list_as_json(payload_to_send):
    return json.dumps(
        payload_to_send,
        sort_keys=False, indent=2)
