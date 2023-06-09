# encoding:utf-8

import json
import os

config = {}
_loaded = False
_config_path = "./.config.json"

def load_config(config_path = _config_path, force=False):
    global config
    global _loaded
    global _config_path
    _config_path = config_path
    if _loaded and not force:
        return config

    if not os.path.exists(config_path):
        raise Exception('no found file:'+config_path)

    config_str = read_file(config_path)
    
    config = json.loads(config_str)
    _loaded = True
    return config


def read_file(path):
    with open(path, mode='r', encoding='utf-8') as f:
        return f.read()


config = load_config()

