import os
import json


def GET_SECRET_KEYS(file_path: str, tag_name: str):
    with open(file_path) as f:
        secrets = json.loads(f.read())
        
    try:
        return secrets[tag_name]
    except KeyError:
        error_msg = "Set the {} environment variable".format(tag_name)
        print(f'{error_msg}')
        