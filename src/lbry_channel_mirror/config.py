import sys
import os
import yaml
import logging

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

def load(directory=os.curdir, name="lbry_mirror.yaml"):
    path = os.path.abspath(os.path.join(directory, name))
    config_errors = []
    try:
        data = open(path).read()
        config = yaml.load(data, Loader=Loader)
        logging.info("Loaded config file: {}".format(path))
    except IOError:
        logging.warn("Could not open config: {}".format(path))
        config = {}

    if config is None:
        config = {}

    return config
