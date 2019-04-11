from lbry_channel_mirror import config as Config
import mimetypes

def get_channel_id(client, config):
    channel_name = config['channel']
    channel = next(client.resolve({"urls": [channel_name]}))
    try:
        channel_id = channel[channel_name]['certificate']['claim_id']
    except KeyError:
        raise RuntimeError("Could not find channel_id for {c}".format(
            c=channel_name))
    return channel_id

def fetch(client, config):
    """Gather new claims from the blockchain, and write them to the config file"""
    channel_id = get_channel_id(client, config)
    claims = []
    for claim in client.claim_search({"channel_id": channel_id}):
        claims.extend(claim['items'])

    if not hasattr(config, "mirror_ids"):
        config['mirror_ids'] = []

    mirror_ids = set(config['mirror_ids'])

    for claim in claims:
        mirror_ids.add(claim['claim_id'])
    config['mirror_ids'] = list(mirror_ids)

    Config.save(config)

def pull(client, config):
    """Download configured files if not existing locally"""
    channel_name = config['channel']
    channel_id = get_channel_id(client, config)

    claims = {} # name -> claim
    for claim_id in config['mirror_ids']:
        claim = next(client.claim_search({"claim_id": claim_id}))
        for i in claim['items']:
            claims["{chan}/{name}".format(chan=channel_name, name=i['name'])] = i

    for name, claim in claims.items():
        f = next(client.file_list({"claim_name": name}))
        if len(f) == 0:
            # Download the file
            filename = "{name}.{ext}".format(
                name= claim['name'],
                ext=mimetypes.guess_extension(claim['value']['stream']['media_type']))
            res = next(client.get({"uri": name, "file_name": filename}))
