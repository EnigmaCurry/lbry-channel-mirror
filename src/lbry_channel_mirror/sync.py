from lbry_channel_mirror import config as Config
import os
import shutil
import mimetypes
import time
import logging

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
    remote_claims = []
    for remote_claim in client.claim_search({"channel_id": channel_id}):
        remote_claims.extend(remote_claim['items'])

    if not hasattr(config, "claims"):
        config['claims'] = {}

    for remote_claim in remote_claims:
        filename = "{name}{ext}".format(
            name=remote_claim['name'],
            ext=mimetypes.guess_extension(remote_claim['value']['stream']['media_type']))
        config['claims'][remote_claim['claim_id']] = {'file_name': filename}

    Config.save(config)

def pull(client, config):
    """Download configured files if not existing locally"""
    channel_name = config['channel']
    channel_id = get_channel_id(client, config)
    remote_claims = {} # name -> claim
    for claim_id in config['claims'].keys():
        claim = next(client.claim_search({"claim_id": claim_id}))
        for i in claim['items']:
            remote_claims[claim_id] = i

    downloads = {} # claim_id -> file_list response
    for claim_id, claim in remote_claims.items():
        download_exists = len(next(client.file_list({"claim_id": claim_id}))) > 0
        filename = config['claims'][claim_id]['file_name']
        if not os.path.exists(os.path.join(config['download_directory'], filename)):
            # Download the file
            if not download_exists:
                logging.info("Starting Download: {f}".format(f=filename))
            downloads[claim['claim_id']] = next(client.get({"uri": claim['name']}))

    # Wait for downloads to finish, then copy to the final directory:
    while len(downloads):
        for claim_id, dl in list(downloads.items()):
            filename = config['claims'][claim_id]['file_name']
            if dl['blobs_remaining'] == 0:
                # Complete:
                # Copy to file destination:
                dest_path = os.path.join(
                    config['download_directory'], filename)
                shutil.copy(dl['download_path'], dest_path)
                # Delete temporary download:
                if next(client.file_delete({'claim_id': claim_id})):
                    logging.debug("Deleted temporary download: {f}".format(f=dl['download_path']))
                else:
                    logging.warn("Failed to delete temporary downloaded file: {f}".format(
                        dl['download_path']))

                del downloads[claim_id]
                logging.info("Download Complete: {f}".format(f=filename))
            else:
                downloads[claim_id] = next(client.file_list({"claim_id": claim_id}))[0]
                logging.info("Download Progress: {f} - blobs remaining: {blobs}".format(
                    f=filename, blobs=dl['blobs_remaining']))
                if dl['blobs_remaining'] > 0:
                    time.sleep(10)

