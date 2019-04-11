import sys
import os
import yaml
import logging
from lbry_channel_mirror.sync import get_channel_id

log = logging.getLogger("config")

class ConfigError(Exception):
    pass

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

EPHEMERAL_CONFIG_KEYS = ['config_path', 'download_directory']
DEFAULT_CONFIG_NAME = "lbry_channel_mirror.yaml"

def load(directory=os.curdir, name=DEFAULT_CONFIG_NAME, required=True):
    path = os.path.abspath(os.path.join(directory, name))
    config_errors = []
    try:
        with open(path) as f:
            data = f.read()
        config = yaml.load(data, Loader=Loader)
        log.info("Loaded config file: {p}".format(p=path))
    except IOError:
        if required:
            log.error("Could not open config: {p}".format(p=path))
            sys.exit(1)
        else:
            log.warn("Could not open config: {p}".format(p=path))
        config = {}

    if config is None:
        config = {}

    config['config_path'] = path
    config['download_directory'] = os.path.dirname(path)

    return config

def save(config, is_new=False):
    if not is_new and not os.path.exists(config['config_path']):
        raise ConfigError("Could not find existing config file: {p}".format(p=config['config_path']))

    path = config['config_path']
    config_copy = dict(config)
    for key in EPHEMERAL_CONFIG_KEYS:
        try:
            del config_copy[key]
        except:
            pass

    with open(path, 'w') as f:
        f.write(yaml.dump(config_copy))
    log.info("Config file saved: {p}".format(p=path))

def init(client, directory, channel):
    """Initialize a directory by creating a new config file"""
    if not channel.startswith("@"):
        raise ConfigError("Channel name must start with @")

    config_path = os.path.abspath(os.path.join(os.curdir, DEFAULT_CONFIG_NAME))
    if os.path.exists(config_path):
        raise ConfigError("Cannot initialize, configuration already exists: {p}".format(p=config_path))

    if "#" not in channel:
        claim_id = get_channel_id(client, channel)
        orig_channel = channel
        channel = "{c}#{id}".format(c=channel, id=claim_id)
        log.warn("Translating channel name from {o} to {c}".format(o=orig_channel, c=channel))

    config = {"channel": channel, "config_path": config_path}
    save(config, is_new=True)
