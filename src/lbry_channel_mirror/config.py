import sys
import os
import yaml
import logging

class ConfigError(Exception):
    pass

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

EPHEMERAL_CONFIG_KEYS = ['config_path', 'download_directory']

def load(directory=os.curdir, name="lbry_channel_mirror.yaml"):
    path = os.path.abspath(os.path.join(directory, name))
    config_errors = []
    try:
        with open(path) as f:
            data = f.read()
        config = yaml.load(data, Loader=Loader)
        logging.info("Loaded config file: {p}".format(p=path))
    except IOError:
        logging.warn("Could not open config: {p}".format(p=path))
        config = {}

    if config is None:
        config = {}

    config['config_path'] = path
    config['download_directory'] = os.path.dirname(path)

    return config

def save(config):
    if not os.path.exists(config['config_path']):
        raise ConfigError("Could not find existing config file: {p}".format(p=path))

    path = config['config_path']
    for key in EPHEMERAL_CONFIG_KEYS:
        del config[key]

    with open(path, 'w') as f:
        f.write(yaml.dump(config))
    logging.info("Config file saved: {p}".format(p=path))

