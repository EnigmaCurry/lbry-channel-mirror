import os
import yaml
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
    except IOError:
        print("Could not open config: {}".format(path))
        exit(1)

    print("Loaded config file: {}".format(path))
    if config is None:
        print("Configuration file is empty.")
        exit(1)

    ## Check for required parameters in config file:
    req_params = {
        "channel": "The LBRY channel to mirror"
    }
    for param, error in req_params.items():
        if param not in config:
            config_errors.append(
                "Missing parameter from config: {} - {}".format(param, error))
    if len(config_errors) > 0:
        for e in config_errors:
            print(e)
        exit(1)
    else:
        return config
